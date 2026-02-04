"""
pytest conftest.py for FastAPI projects
Place this in your project root or tests/ directory
"""

import os
import sys
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, Mock

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import your FastAPI app (adjust import as needed)
try:
    from main import app
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
    from app.models import Base
    from app.database import get_db
except ImportError:
    # These will be imported when the conftest is actually used
    app = None
    Base = None
    get_db = None


# =============================================================================
# Database Fixtures
# =============================================================================

# Test database URL (use SQLite for fast tests)
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    os.remove("./test.db") if os.path.exists("./test.db") else None


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_client(test_db):
    """Create a test client with database override."""
    if app is None:
        pytest.skip("FastAPI app not available")

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


# =============================================================================
# HTTP Client Fixtures
# =============================================================================

@pytest.fixture
def client():
    """Standard TestClient for FastAPI."""
    if app is None:
        pytest.skip("FastAPI app not available")
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async client for testing FastAPI endpoints."""
    if app is None:
        pytest.skip("FastAPI app not available")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


# =============================================================================
# Authentication Fixtures
# =============================================================================

@pytest.fixture
def test_user_token():
    """Generate a test JWT token."""
    # Adjust this based on your auth implementation
    from datetime import datetime, timedelta
    import jwt

    payload = {
        "sub": "testuser",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "user_id": 1
    }

    # Use your actual secret key or override in settings
    secret = "test_secret_key"
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.fixture
def auth_headers(test_user_token):
    """Headers with authentication token."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def authenticated_client(client, auth_headers):
    """Client with authentication headers."""
    client.headers.update(auth_headers)
    return client


@pytest.fixture
async def async_authenticated_client(async_client, auth_headers):
    """Async client with authentication headers."""
    async_client.headers.update(auth_headers)
    return async_client


# =============================================================================
# User Factory Fixtures
# =============================================================================

@pytest.fixture
def make_user(test_db):
    """Factory for creating test users."""
    def _make_user(**kwargs):
        from app.models import User
        defaults = {
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": "hashed_password_here",
            "is_active": True
        }
        defaults.update(kwargs)

        user = User(**defaults)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user

    return _make_user


@pytest.fixture
def user(test_db, make_user):
    """Create a default test user."""
    return make_user(username="testuser", email="test@example.com")


@pytest.fixture
def admin_user(test_db):
    """Create an admin user."""
    from app.models import User
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=True
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


# =============================================================================
# Model Factory Fixtures
# =============================================================================

class ModelFactory:
    """Helper class for creating model instances."""

    def __init__(self, model_class, db_session, **defaults):
        self.model_class = model_class
        self.db = db_session
        self.defaults = defaults

    def create(self, **kwargs):
        """Create a model instance."""
        params = {**self.defaults, **kwargs}
        instance = self.model_class(**params)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def create_batch(self, count, **kwargs):
        """Create multiple instances."""
        return [self.create(**kwargs) for _ in range(count)]


@pytest.fixture
def model_factory(test_db):
    """Factory fixture for creating any model instance."""
    def _factory(model_class, **defaults):
        return ModelFactory(model_class, test_db, **defaults)
    return _factory


# =============================================================================
# API Response Helpers
# =============================================================================

@pytest.fixture
def api_helpers():
    """Helper methods for API testing."""
    class Helpers:
        @staticmethod
        def assert_success(response, status_code=200):
            assert response.status_code == status_code, \
                f"Expected {status_code}, got {response.status_code}: {response.text}"

        @staticmethod
        def assert_created(response):
            assert response.status_code == 201, \
                f"Expected 201, got {response.status_code}: {response.text}"

        @staticmethod
        def assert_no_content(response):
            assert response.status_code == 204, \
                f"Expected 204, got {response.status_code}: {response.text}"

        @staticmethod
        def assert_error(response, status_code=400):
            assert response.status_code == status_code, \
                f"Expected {status_code}, got {response.status_code}: {response.text}"

        @staticmethod
        def assert_validation_error(response):
            assert response.status_code == 422, \
                f"Expected 422, got {response.status_code}: {response.text}"

        @staticmethod
        def get_json(response):
            return response.json()

        @staticmethod
        def assert_json_keys(response, *keys):
            data = response.json()
            for key in keys:
                assert key in data, f"Key '{key}' not found in response: {data}"

    return Helpers


# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_external_service(monkeypatch):
    """Mock external service."""
    mock = AsyncMock()
    mock.get_data.return_value = {"result": "success"}
    return mock


@pytest.fixture
def mock_cache(monkeypatch):
    """Mock cache service."""
    from unittest.mock import Mock
    mock_cache = Mock()
    mock_cache.get.return_value = None
    mock_cache.set.return_value = True
    mock_cache.delete.return_value = True
    return mock_cache


@pytest.fixture
def mock_background_tasks(monkeypatch):
    """Mock background tasks."""
    from unittest.mock import Mock
    mock_tasks = Mock()
    return mock_tasks


# =============================================================================
# File Upload Fixtures
# =============================================================================

@pytest.fixture
def sample_image():
    """Create a sample image for upload tests."""
    from io import BytesIO
    from PIL import Image

    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    return img_io


@pytest.fixture
def sample_file():
    """Create a sample file for upload tests."""
    from io import BytesIO
    file_io = BytesIO(b"test file content")
    return file_io


# =============================================================================
# Email Testing
# =============================================================================

@pytest.fixture
def email_monitor():
    """Monitor emails sent during tests."""
    sent_emails = []

    class MockEmailService:
        def send(self, to: str, subject: str, body: str):
            sent_emails.append({
                "to": to,
                "subject": subject,
                "body": body
            })

    return MockEmailService(), sent_emails


# =============================================================================
# Time Testing
# =============================================================================

@pytest.fixture
def freeze_time():
    """Context manager for freezing time."""
    from freezegun import freeze_time

    def _freeze(dt_str=None):
        if dt_str is None:
            dt_str = "2024-01-01 12:00:00"
        return freeze_time(dt_str)

    return _freeze


# =============================================================================
# WebSocket Testing
# =============================================================================

@pytest.fixture
def ws_client():
    """WebSocket client for testing."""
    from fastapi.testclient import TestClient
    if app is None:
        pytest.skip("FastAPI app not available")

    client = TestClient(app)
    return client


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_payload():
    """Generic sample payload for POST requests."""
    return {
        "name": "Test Item",
        "description": "Test description",
        "value": 100,
        "active": True
    }


@pytest.fixture
def sample_items(test_db):
    """Create sample items in database."""
    from app.models import Item  # Adjust import
    items = [
        Item(name=f"Item {i}", value=i * 10)
        for i in range(1, 6)
    ]
    test_db.add_all(items)
    test_db.commit()
    return items


# =============================================================================
# Configuration & Hooks
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, no external dependencies)")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "async: Async tests")
    config.addinivalue_line("markers", "auth: Tests requiring authentication")


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers."""
    for item in items:
        # Add async marker to async tests
        if asyncio.iscoroutinefunction(item.obj):
            item.add_marker(pytest.mark.asyncio)


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
    parser.addoption(
        "--skip-auth",
        action="store_true",
        default=False,
        help="Skip authentication tests"


def pytest_runtest_setup(item):
    """Skip tests based on conditions."""
    if "slow" in item.keywords and not item.config.getoption("--run-slow"):
        pytest.skip("Skipping slow tests (use --run-slow to include)")

    if "integration" in item.keywords and not item.config.getoption("--integration"):
        pytest.skip("Skipping integration tests (use --integration to include)")


# Import asyncio for async test detection
import asyncio
