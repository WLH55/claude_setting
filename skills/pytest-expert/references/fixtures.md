# pytest Fixtures Patterns

## Fixture Basics

```python
import pytest

# Simple fixture
@pytest.fixture
def sample_data():
    return {"key": "value", "number": 42}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
    assert sample_data["number"] == 42

# Fixture with setup/teardown
@pytest.fixture
def resource():
    # Setup: create resource
    obj = Resource()
    obj.initialize()
    yield obj
    # Teardown: cleanup
    obj.cleanup()

def test_with_resource(resource):
    assert resource.is_ready()
```

## Fixture Scopes

```python
# function scope (default) - runs for each test
@pytest.fixture(scope="function")
def db_connection():
    conn = connect()
    yield conn
    conn.close()

# class scope - runs once per test class
@pytest.fixture(scope="class")
def class_resource():
    obj = Resource()
    yield obj
    obj.cleanup()

# module scope - runs once per module
@pytest.fixture(scope="module")
def module_cache():
    cache = Cache()
    cache.warm_up()
    yield cache
    cache.clear()

# session scope - runs once per test session
@pytest.fixture(scope="session")
def global_config():
    config = load_config()
    yield config
```

## Fixture with Parameters

```python
@pytest.fixture(params=["value1", "value2", "value3"])
def parametrized_data(request):
    return request.param

def test_with_params(parametrized_data):
    assert parametrized_data in ["value1", "value2", "value3"]

# Parametrized with IDs
@pytest.fixture(
    params=[
        ("user", "password"),
        ("admin", "admin123")
    ],
    ids=["regular-user", "admin-user"]
)
def credentials(request):
    return request.param

def test_login(credentials):
    username, password = credentials
    # Test with different credentials
```

## Fixture Dependency

```python
@pytest.fixture
def database():
    return Database()

@pytest.fixture
def user(database):
    return database.create_user()

@pytest.fixture
def posts(user):
    return [user.create_post(f"Post {i}") for i in range(5)]

def test_user_posts(posts):
    # posts fixture depends on user, which depends on database
    assert len(posts) == 5
```

## Using Fixtures in Fixtures

```python
@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client):
    token = api_client.login("user", "pass")
    api_client.set_auth_token(token)
    yield api_client
    api_client.logout()

def test_authenticated_request(authenticated_client):
    response = authenticated_client.get("/protected/")
    assert response.status_code == 200
```

## Class-based Fixtures

```python
@pytest.fixture(scope="class")
def class_setup(request):
    # Setup
    request.cls.resource = Resource()
    request.cls.resource.initialize()
    yield
    # Teardown
    request.cls.resource.cleanup()

@pytest.mark.usefixtures("class_setup")
class TestResource:
    def test_has_resource(self):
        assert hasattr(self, "resource")
        assert self.resource.is_ready()

    def test_resource_usage(self):
        self.resource.do_something()
```

## Autouse Fixtures (Auto-applied)

```python
# Runs before every test in the module
@pytest.fixture(autouse=True)
def reset_state():
    state.reset()
    yield
    state.cleanup()

def test_one():
    # state was reset before this test
    pass

def test_two():
    # state was reset before this test too
    pass
```

## Conditional Fixtures

```python
@pytest.fixture
def slow_service(request):
    if request.config.getoption("--run-slow"):
        return SlowService()
    return MockService()

def test_with_service(slow_service):
    # Use real service if --run-slow flag is used
    result = slow_service.process()
```

## Fixture Factories

```python
@pytest.fixture
def make_user():
    def _make_user(**kwargs):
        defaults = {"username": "test", "email": "test@example.com"}
        defaults.update(kwargs)
        return User.objects.create(**defaults)
    return _make_user

def test_create_users(make_user):
    user1 = make_user(username="user1")
    user2 = make_user(username="user2", email="user2@example.com")
    assert user1.username == "user1"
    assert user2.email == "user2@example.com"
```

## Django-specific Fixtures

```python
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user(db):
    """Create a regular user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )

@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="admin123"
    )

@pytest.fixture
def users(db):
    """Create multiple users."""
    return [
        User.objects.create_user(username=f"user{i}", email=f"user{i}@example.com")
        for i in range(10)
    ]

@pytest.fixture
def authenticated_client(client, user):
    """Client with authenticated user."""
    client.force_login(user)
    return client

@pytest.fixture
def api_client_with_token(client, user):
    """API client with Bearer token."""
    from rest_framework_simplejwt.tokens import RefreshToken
    token = RefreshToken.for_user(user)
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token.access_token}"
    return client
```

## Database-related Fixtures

```python
@pytest.fixture
def empty_db(db):
    """Empty database with only schema."""
    MyModel.objects.all().delete()
    yield

@pytest.fixture
def sample_objects(db):
    """Pre-populate database with sample data."""
    objects = [
        MyModel.objects.create(name=f"Item {i}")
        for i in range(5)
    ]
    yield objects
    # Cleanup
    MyModel.objects.all().delete()

@pytest.fixture
def django_db_reset(db):
    """Reset database sequences."""
    from django.core.management import call_command
    call_command('sqlsequencereset', 'myapp')
```

## API Testing Fixtures

```python
@pytest.fixture
def api_response(client):
    """Make API call and return response."""
    def _make_request(method, endpoint, data=None):
        if method == "GET":
            return client.get(endpoint)
        elif method == "POST":
            return client.post(endpoint, data, content_type="application/json")
    return _make_request

@pytest.fixture
def mock_external_service(monkeypatch):
    """Mock external service with configurable response."""
    def _mock(return_value):
        monkeypatch.setattr(
            "module.external_service.call",
            lambda: return_value
        )
    return _mock
```

## Time-based Fixtures

```python
from datetime import datetime, timedelta
from freezegun import freeze_time

@pytest.fixture
def frozen_time():
    """Freeze time to a specific moment."""
    with freeze_time("2024-01-01 12:00:00"):
        yield datetime(2024, 1, 1, 12, 0, 0)

@pytest.fixture
def travel_to():
    """Time travel context manager."""
    def _travel_to(dt_str):
        return freeze_time(dt_str)
    return _travel_to

def test_with_frozen_time(frozen_time):
    assert datetime.now() == frozen_time

def test_time_travel(travel_to):
    with travel_to("2024-12-31 23:59:59"):
        assert datetime.now().year == 2024
```

## File/IO Fixtures

```python
import tempfile
import os

@pytest.fixture
def temp_file():
    """Create a temporary file."""
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, 'w') as f:
        f.write("test content")
    yield path
    os.unlink(path)

@pytest.fixture
def temp_directory():
    """Create a temporary directory."""
    path = tempfile.mkdtemp()
    yield path
    # Cleanup
    import shutil
    shutil.rmtree(path)

@pytest.fixture
def sample_csv(temp_file):
    """Create a sample CSV file."""
    import csv
    with open(temp_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["name", "age"])
        writer.writerow(["Alice", 30])
        writer.writerow(["Bob", 25])
    yield temp_file
```

## Mock Fixtures

```python
from unittest.mock import Mock, patch, MagicMock

@pytest.fixture
def mock_api():
    """Mock API client."""
    mock = Mock()
    mock.get.return_value.json.return_value = {"data": "test"}
    return mock

@pytest.fixture
def mock_external_service(monkeypatch):
    """Mock external service."""
    mock = MagicMock()
    mock.process.return_value = "processed"
    monkeypatch.setattr("module.Service", lambda: mock)
    return mock

@pytest.fixture
def patched_environment(monkeypatch):
    """Patch environment variables."""
    monkeypatch.setenv("API_KEY", "test_key")
    monkeypatch.setenv("DEBUG", "true")
    yield
```

## Logging Fixtures

```python
import logging

@pytest.fixture
def capture_logs(caplog):
    """Capture log output."""
    caplog.set_level(logging.DEBUG)
    return caplog

def test_logging(capture_logs):
    logging.info("Test message")
    assert "Test message" in capture_logs.text
```

## Configuration Fixtures

```python
@pytest.fixture
def test_settings(monkeypatch, settings):
    """Override Django settings for tests."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.DEBUG = False
    yield settings
```

## Request Object in Fixtures

```python
@pytest.fixture
def check_test_name(request):
    """Access test node information."""
    print(f"Running test: {request.node.name}")
    print(f"Module: {request.module.__name__}")
    print(f"Function: {request.function.__name__}")
    print(f"Markers: {request.node.keywords}")

@pytest.fixture
def skip_if_slow(request):
    """Skip test based on marker."""
    if "slow" in request.node.keywords:
        if not request.config.getoption("--run-slow"):
            pytest.skip("Skipping slow tests")
```

## Conftest.py Organization

```python
# conftest.py - project root
@pytest.fixture(scope="session")
def global_config():
    """Shared across all tests."""
    return load_test_config()

# app/tests/conftest.py
@pytest.fixture(scope="module")
def app_config():
    """Shared within app tests."""
    return load_app_config()

# app/tests/test_views/conftest.py
@pytest.fixture
def view_data():
    """Specific to view tests."""
    return {"test": "data"}
```

## Common Fixture Patterns

```python
# Pattern 1: Setup-Teardown
@pytest.fixture
def with_setup():
    resource = setup()
    yield resource
    teardown(resource)

# Pattern 2: Cached
@pytest.fixture(scope="session")
def expensive_resource():
    # Only created once
    return ExpensiveResource()

# Pattern 3: Factory
@pytest.fixture
def make_object():
    def _make(**kwargs):
        return MyModel(**kwargs)
    return _make

# Pattern 4: Parametrized
@pytest.fixture(params=["redis", "memcached"])
def cache_backend(request):
    return CacheBackend(request.param)

# Pattern 5: Lazy
@pytest.fixture
def lazy_resource():
    def _create():
        return Resource()
    return _create
```
