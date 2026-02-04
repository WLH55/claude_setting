"""
pytest conftest.py for Django projects
Place this in your project root or tests/ directory
"""

import os
import sys
import django
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient

User = get_user_model()


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def db(db):
    """
    Alias for pytest-django's db fixture.
    Use this for tests that need database access.
    """
    return db


@pytest.fixture(scope="function")
def db_reset(db):
    """
    Reset database sequences for tests.
    Useful when you need clean IDs.
    """
    from django.core.management import call_command
    call_command('sqlsequencereset', *django.apps.apps.app_configs.keys())
    yield


# =============================================================================
# User Fixtures
# =============================================================================

@pytest.fixture
def user(db):
    """Create a regular user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User"
    )


@pytest.fixture
def user2(db):
    """Create a second regular user."""
    return User.objects.create_user(
        username="testuser2",
        email="test2@example.com",
        password="testpass123"
    )


@pytest.fixture
def admin_user(db):
    """Create an admin/superuser."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="admin123",
        first_name="Admin",
        last_name="User"
    )


@pytest.fixture
def users(db):
    """Create multiple users for testing."""
    return [
        User.objects.create_user(
            username=f"user{i}",
            email=f"user{i}@example.com",
            password="password123"
        )
        for i in range(1, 6)
    ]


# =============================================================================
# Client Fixtures
# =============================================================================

@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def authenticated_client(client, user):
    """Client with authenticated user session."""
    client.force_login(user)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Client with admin user session."""
    client.force_login(admin_user)
    return client


@pytest.fixture
def api_client():
    """Django REST framework API client."""
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, user):
    """API client with authenticated user."""
    from rest_framework_simplejwt.tokens import RefreshToken
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    return api_client


@pytest.fixture
def admin_api_client(api_client, admin_user):
    """API client with admin user."""
    from rest_framework_simplejwt.tokens import RefreshToken
    token = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    return api_client


# =============================================================================
# Model Factory Fixtures
# =============================================================================

class ModelFactory:
    """Helper class for creating model instances."""

    def __init__(self, model_class, **defaults):
        self.model_class = model_class
        self.defaults = defaults

    def create(self, **kwargs):
        """Create a model instance with merged defaults and kwargs."""
        params = {**self.defaults, **kwargs}
        return self.model_class.objects.create(**params)

    def create_batch(self, count, **kwargs):
        """Create multiple instances."""
        return [self.create(**kwargs) for _ in range(count)]


@pytest.fixture
def make_user(db):
    """Factory fixture for creating users with custom attributes."""
    def _make_user(**kwargs):
        defaults = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return _make_user


# =============================================================================
# API Response Helpers
# =============================================================================

@pytest.fixture
def api_response_helpers():
    """Helper methods for API testing."""
    class Helpers:
        @staticmethod
        def assert_success(response, status_code=200):
            """Assert API response was successful."""
            assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}: {response.content}"

        @staticmethod
        def assert_created(response):
            """Assert resource was created."""
            assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.content}"

        @staticmethod
        def assert_no_content(response):
            """Assert no content response."""
            assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.content}"

        @staticmethod
        def assert_error(response, status_code=400):
            """Assert API returned an error."""
            assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}: {response.content}"

        @staticmethod
        def get_data(response):
            """Get JSON data from response."""
            return response.json()

    return Helpers


# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_cache(monkeypatch):
    """Mock Django cache for testing."""
    from unittest.mock import Mock
    mock_cache = Mock()
    mock_cache.get.return_value = None
    mock_cache.set.return_value = True
    mock_cache.delete.return_value = True
    monkeypatch.setattr("django.core.cache.cache", mock_cache)
    return mock_cache


@pytest.fixture
def mock_settings(monkeypatch, settings):
    """Override Django settings for tests."""
    def _override(**kwargs):
        for key, value in kwargs.items():
            setattr(settings, key, value)
    return _override


# =============================================================================
# Email Testing
# =============================================================================

@pytest.fixture
def email_backend(settings):
    """Configure email backend for testing."""
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    from django.core import mail
    mail.outbox = []
    return mail


# =============================================================================
# Time Testing
# =============================================================================

@pytest.fixture
def freeze_time():
    """Context manager for freezing time in tests."""
    from freezegun import freeze_time
    from datetime import datetime

    def _freeze(dt_str=None):
        if dt_str is None:
            dt_str = "2024-01-01 12:00:00"
        return freeze_time(dt_str)

    return _freeze


# =============================================================================
# File Upload Testing
# =============================================================================

@pytest.fixture
def sample_image():
    """Create a sample image file for upload testing."""
    from django.core.files.uploadedfile import SimpleUploadedFile
    return SimpleUploadedFile(
        "test_image.jpg",
        b"fake image data here",
        content_type="image/jpeg"
    )


@pytest.fixture
def sample_file():
    """Create a sample text file for upload testing."""
    from django.core.files.uploadedfile import SimpleUploadedFile
    return SimpleUploadedFile(
        "test_file.txt",
        b"test file content",
        content_type="text/plain"
    )


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_data():
    """Generic sample data dictionary."""
    return {
        "name": "Test Item",
        "description": "Test description",
        "value": 100,
        "active": True
    }


# =============================================================================
# Hooks and Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


@pytest.fixture(scope="session", autouse=True)
def enable_db_access():
    """Enable database access for all tests."""
    # This ensures Django is set up before any tests run
    pass


@pytest.fixture(autouse=True)
def reset_caches(db):
    """Reset Django caches between tests."""
    from django.core.cache import caches
    for cache in caches.all():
        cache.clear()
    yield
    for cache in caches.all():
        cache.clear()


# =============================================================================
# Skip tests based on conditions
# =============================================================================

def pytest_runtest_setup(item):
    """Skip tests based on markers and conditions."""
    if "slow" in item.keywords and not item.config.getoption("--run-slow"):
        pytest.skip("Skipping slow tests (use --run-slow to include)")


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests"
    )
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests"
    )
