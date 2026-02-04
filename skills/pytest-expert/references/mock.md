# Mocking External Services

## Basic Mock with unittest.mock

```python
from unittest.mock import Mock, patch, MagicMock, call

# Create a simple mock
mock_service = Mock()
mock_service.get_data.return_value = {"result": "success"}

result = mock_service.get_data()
assert result == {"result": "success"}

# Verify method was called
mock_service.get_data.assert_called_once()

# Verify with specific arguments
mock_service.process(item_id=123)
mock_service.process.assert_called_with(item_id=123)

# Configure multiple return values
mock.fetch.side_effect = ["result1", "result2", "result3"]
assert mock.fetch() == "result1"
assert mock.fetch() == "result2"

# Raise exception
mock.save.side_effect = ValueError("Invalid data")
with pytest.raises(ValueError):
    mock.save({"invalid": "data"})
```

## Patching with Decorators

```python
from unittest.mock import patch

# Patch a module attribute
@patch("module.external_api_call")
def test_with_mock(mock_api):
    mock_api.return_value = {"status": "ok"}
    result = module.my_function()
    assert result["status"] == "ok"

# Patch with context manager
def test_with_context_manager():
    with patch("module.external_api_call") as mock_api:
        mock_api.return_value = {"status": "ok"}
        result = module.my_function()
        assert result["status"] == "ok"]

# Patch multiple things
@patch("module.API_KEY", "test_key")
@patch("module.external_call")
def test_multiple_patches(mock_call, mock_key):
    mock_call.return_value = "data"
    result = module.function()
    assert mock_call.called

# Use patch.object for objects
@patch.object(MyClass, 'method_name')
def test_patch_object(mock_method):
    mock_method.return_value = "mocked"
    obj = MyClass()
    assert obj.method_name() == "mocked"
```

## Mocking HTTP Requests (requests)

```python
import requests
from unittest.mock import patch, Mock

@patch("requests.get")
def test_http_get(mock_get):
    # Configure mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value = mock_response

    # Test
    response = requests.get("https://api.example.com/data")
    assert response.status_code == 200
    assert response.json()["data"] == "test"

    # Verify correct URL was called
    mock_get.assert_called_with("https://api.example.com/data")

# With responses library
import responses

@responses.activate
def test_with_responses():
    responses.add(
        responses.GET,
        "https://api.example.com/data",
        json={"result": "success"},
        status=200
    )

    response = requests.get("https://api.example.com/data")
    assert response.json() == {"result": "success"}
```

## Mocking HTTPX (for FastAPI async)

```python
import httpx
from unittest.mock import patch, AsyncMock

@patch("httpx.AsyncClient.get")
async def test_httpx_mock(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={"data": "test"})
    mock_get.return_value = mock_response

    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
        assert response.status_code == 200

# With respx library
import pytest
import respx

@pytest.mark.asyncio
@respx.mock
async def test_with_respx():
    respx.get("https://api.example.com/data").mock(
        return_value=httpx.Response(200, json={"result": "success"})
    )

    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        assert response.json() == {"result": "success"}
```

## Mocking Django ORM Queries

```python
from unittest.mock import patch

@patch("myapp.models.MyModel.objects.filter")
def test_queryset_mock(mock_filter):
    # Create mock queryset
    mock_queryset = Mock()
    mock_queryset.count.return_value = 5
    mock_filter.return_value = mock_queryset

    # Test
    count = myapp.models.MyModel.objects.filter(active=True).count()
    assert count == 5
    mock_filter.assert_called_with(active=True)

# Mock specific manager methods
@patch("myapp.models.MyModel.objects.get")
def test_model_get(mock_get):
    mock_obj = Mock(id=1, name="Test")
    mock_get.return_value = mock_obj

    obj = myapp.models.MyModel.objects.get(id=1)
    assert obj.name == "Test"
```

## Mocking External APIs (Google Play, AWS, etc.)

```python
# Mock Google Play Service
@patch("vps.utils.gp.GooglePlayService.get_androidpublisher_token")
def test_vps_with_mock_gp_token(mock_token, client):
    mock_token.return_value = "fake_token_123"

    response = client.get("/api/vps/crash-rate/", {
        "package_name": "com.example.app",
        "days": 7
    })

    assert response.status_code == 200
    mock_token.assert_called_once()

# Mock AWS S3
@patch("boto3.client")
def test_s3_upload(mock_boto3_client):
    mock_s3 = Mock()
    mock_boto3_client.return_value = mock_s3

    upload_file_to_s3("file.txt", "bucket", "key")

    mock_s3.upload_file.assert_called_with(
        "file.txt", "bucket", "key"
    )

# Mock Redis
@patch("redis.Redis")
def test_redis_cache(mock_redis):
    mock_client = Mock()
    mock_redis.return_value = mock_client
    mock_client.get.return_value = b"cached_value"

    result = get_from_cache("key")
    assert result == "cached_value"
    mock_client.get.assert_called_with("key")
```

## Mocking Database Connections

```python
@patch("psycopg2.connect")
def test_database_query(mock_connect):
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1, "Alice"), (2, "Bob")]
    mock_connect.return_value = mock_conn

    results = fetch_users()
    assert len(results) == 2
    mock_cursor.execute.assert_called()
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()
```

## Mocking File Operations

```python
from unittest.mock import mock_open, patch

@patch("builtins.open", new_callable=mock_open, read_data="file content")
def test_read_file(mock_file):
    content = read_file("test.txt")
    assert content == "file content"
    mock_file.assert_called_with("test.txt", "r")

@patch("builtins.open", new_callable=mock_open)
def test_write_file(mock_file):
    write_file("test.txt", "new content")
    mock_file.assert_called_with("test.txt", "w")
    mock_file().write.assert_called_with("new content")

# Mock os.path operations
@patch("os.path.exists")
@patch("os.makedirs")
def test_directory_creation(mock_makedirs, mock_exists):
    mock_exists.return_value = False

    ensure_directory("/test/path")
    mock_exists.assert_called_with("/test/path")
    mock_makedirs.assert_called_with("/test/path")
```

## Mocking Celery Tasks

```python
from unittest.mock import patch
from myapp.tasks import send_email_task

@patch("myapp.tasks.send_email_task.delay")
def test_task_dispatch(mock_delay):
    mock_delay.return_value = Mock(id="task-123")

    result = send_email_task("user@example.com", "Subject", "Body")

    mock_delay.assert_called_with("user@example.com", "Subject", "Body")

# Test task directly (with eager mode)
@pytest.mark.django_db
@patch.dict("django.conf.settings", {"CELERY_TASK_ALWAYS_EAGER": True})
def test_task_execution():
    task = send_email_task.s("user@example.com", "Subject", "Body")
    result = task.apply()
    assert result.successful()
```

## Mocking Time

```python
from unittest.mock import patch
from datetime import datetime
import freezegun

# Using freezegun
def test_with_freezegun():
    with freezegun.freeze_time("2024-01-01 12:00:00"):
        assert datetime.now() == datetime(2024, 1, 1, 12, 0, 0)

# As fixture
@pytest.fixture
def freeze_at_time():
    with freezegun.freeze_time("2024-12-25"):
        yield datetime(2024, 12, 25)

def test_christmas(freeze_at_time):
    assert datetime.now().month == 12
    assert datetime.now().day == 25
```

## Mocking Environment Variables

```python
import os
from unittest.mock import patch

# Using patch.dict
@patch.dict(os.environ, {"API_KEY": "test_key", "DEBUG": "true"})
def test_with_env():
    assert os.getenv("API_KEY") == "test_key"

# Using monkeypatch (pytest)
def test_with_monkeypatch(monkeypatch):
    monkeypatch.setenv("API_KEY", "test_key")
    monkeypatch.setenv("DEBUG", "true")

    # Your test code here

# Using fixture
@pytest.fixture
def test_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    yield
```

## Mocking Logger

```python
from unittest.mock import patch
import logging

@patch("myapp.logger")
def test_logging(mock_logger):
    process_something()

    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()

# With caplog fixture
def test_with_caplog(caplog):
    caplog.set_level(logging.INFO)
    process_something()
    assert "Processing complete" in caplog.text
```

## Mocking第三方服务

```python
# Mock Stripe
@patch("stripe.Customer.create")
def test_stripe_customer(mock_create):
    mock_create.return_value = Mock(id="cus_123")
    customer = create_stripe_customer("email@example.com")
    assert customer.id == "cus_123"

# Mock SendGrid
@patch("sendgrid.SendGridAPIClient.send")
def test_sendgrid(mock_send):
    mock_send.return_value = Mock(status_code=202)
    result = send_email("to@example.com", "Subject", "Body")
    assert result.status_code == 202

# Mock Twilio
@patch("twilio.rest.Client.messages")
def test_twilio(mock_messages):
    mock_message = Mock(sid="MSG123")
    mock_messages.create.return_value = mock_message
    result = send_sms("+1234567890", "Message")
    assert result.sid == "MSG123"
```

## Auto-speccing mocks

```python
from unittest.mock import create_autospec

# Auto-spec from class
class RealClass:
    def method_one(self):
        pass
    def method_two(self):
        pass

mock_real = create_autospec(RealClass)
mock_real.method_one()  # OK
mock_real.nonexistent()  # Raises AttributeError

# Auto-spec from instance
def test_with_autospec():
    real_obj = RealClass()
    mock_obj = create_autospec(real_obj)
    mock_obj.method_one()
```

## Mock return values based on input

```python
from unittest.mock import Mock

# Side effect with function
def side_effect_func(value):
    if value == "valid":
        return "success"
    else:
        return "failure"

mock_processor = Mock()
mock_processor.process.side_effect = side_effect_func

assert mock_processor.process("valid") == "success"
assert mock_processor.process("invalid") == "failure"

# Side effect with dict lookup
mock_db = Mock()
mock_db.get.side_effect = lambda key: {"key1": "value1", "key2": "value2"}.get(key)

assert mock_db.get("key1") == "value1"
assert mock_db.get("unknown") is None
```

## Mock assertions

```python
# Check if called
mock_func.assert_called()

# Check call count
assert mock_func.call_count == 3

# Check specific call
mock_func.assert_called_with(arg1, arg2, kwarg=value)

# Check any call with
mock_func.assert_any_call("any_value")

# Check never called
mock_func.assert_not_called()

# Check call order
expected_calls = [call(1), call(2), call(3)]
mock_func.assert_has_calls(expected_calls)

# Get call arguments
first_call_args = mock_func.call_args[0]
first_call_kwargs = mock_func.call_args[1]
all_calls = mock_func.call_args_list
```
