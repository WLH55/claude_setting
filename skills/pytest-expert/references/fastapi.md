# FastAPI Testing with pytest

## Test Structure

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello"}

# tests/test_routes.py
def test_create_item(client):
    response = client.post("/api/items/", json={"name": "Test Item"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert "id" in data
```

## FastAPI Fixtures

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Create a test client with the test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers():
    """Generate authentication headers."""
    token = create_test_token()
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def authenticated_client(client, auth_headers):
    """Client with authentication headers."""
    client.headers.update(auth_headers)
    return client
```

## Testing GET Endpoints

```python
def test_list_items(client):
    response = client.get("/api/items/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

def test_get_item_by_id(client, item):
    response = client.get(f"/api/items/{item.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item.id

def test_get_item_not_found(client):
    response = client.get("/api/items/999999")
    assert response.status_code == 404

def test_list_with_pagination(client):
    response = client.get("/api/items/?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 10

def test_list_with_filters(client):
    response = client.get("/api/items/?category=electronics")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["category"] == "electronics"
```

## Testing POST Endpoints

```python
def test_create_item(client):
    payload = {
        "name": "New Item",
        "description": "Test description",
        "price": 99.99
    }
    response = client.post("/api/items/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Item"
    assert data["price"] == 99.99
    assert "id" in data

def test_create_item_validation_error(client):
    payload = {
        "name": "",  # Invalid: empty name
        "price": -10  # Invalid: negative price
    }
    response = client.post("/api/items/", json=payload)
    assert response.status_code == 422

def test_create_item_missing_field(client):
    payload = {"name": "Item"}  # Missing required 'price'
    response = client.post("/api/items/", json=payload)
    assert response.status_code == 422
```

## Testing PUT/PATCH Endpoints

```python
def test_update_item(client, item):
    payload = {"name": "Updated Name"}
    response = client.patch(f"/api/items/{item.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"

def test_update_item_not_found(client):
    payload = {"name": "Updated"}
    response = client.patch("/api/items/999999", json=payload)
    assert response.status_code == 404

def test_full_replace_item(client, item):
    payload = {
        "name": "Replaced",
        "description": "New description",
        "price": 49.99
    }
    response = client.put(f"/api/items/{item.id}", json=payload)
    assert response.status_code == 200
```

## Testing DELETE Endpoints

```python
def test_delete_item(client, item):
    response = client.delete(f"/api/items/{item.id}")
    assert response.status_code == 204

    # Verify deletion
    response = client.get(f"/api/items/{item.id}")
    assert response.status_code == 404

def test_delete_item_not_found(client):
    response = client.delete("/api/items/999999")
    assert response.status_code == 404
```

## Testing Authentication/Authorization

```python
def test_unauthorized_access(client):
    response = client.get("/api/protected/")
    assert response.status_code == 401

def test_with_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/protected/", headers=headers)
    assert response.status_code == 401

def test_authorized_access(authenticated_client):
    response = authenticated_client.get("/api/protected/")
    assert response.status_code == 200

def test_admin_only_endpoint(client, admin_headers):
    response = client.get("/api/admin/users/", headers=admin_headers)
    assert response.status_code == 200

def test_admin_endpoint_forbidden(client, user_headers):
    response = client.get("/api/admin/users/", headers=user_headers)
    assert response.status_code == 403
```

## Testing Dependency Injection

```python
from unittest.mock import Mock

def test_with_mocked_dependency(client):
    # Mock a dependency
    mock_service = Mock()
    mock_service.get_data.return_value = {"result": "mocked"}

    app.dependency_overrides[get_external_service] = lambda: mock_service

    response = client.get("/api/external/")
    assert response.status_code == 200
    assert response.json()["result"] == "mocked"

    app.dependency_overrides.clear()
```

## Testing File Uploads

```python
def test_upload_file(client):
    file_content = b"file content here"
    files = {"file": ("test.txt", file_content, "text/plain")}

    response = client.post("/api/upload/", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.txt"

def test_upload_multiple_files(client):
    files = [
        ("files", ("file1.txt", b"content1", "text/plain")),
        ("files", ("file2.txt", b"content2", "text/plain"))
    ]

    response = client.post("/api/upload/multiple/", files=files)
    assert response.status_code == 201
```

## Testing WebSocket

```python
from fastapi.testclient import TestClient

def test_websocket(client):
    with client.websocket_connect("/ws/items") as websocket:
        websocket.send_text("ping")
        data = websocket.receive_text()
        assert data == "pong"

def test_websocket_authentication(client):
    # Test WebSocket with token in query param
    with client.websocket_connect(
        "/ws?token=test_token"
    ) as websocket:
        websocket.send_json({"action": "subscribe", "channel": "updates"})
        response = websocket.receive_json()
        assert response["status"] == "subscribed"
```

## Testing Background Tasks

```python
def test_background_task(client):
    response = client.post("/api/email/", json={"to": "test@example.com"})
    assert response.status_code == 202

    # Wait for background task to complete
    import time
    time.sleep(0.1)

    # Verify email was sent
    assert len(outbox) == 1
```

## Testing Exception Handlers

```python
def test_custom_exception_handler(client):
    response = client.get("/api/error/")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Custom error message" in data["detail"]

def test_validation_exception(client):
    response = client.post("/api/items/", json={"invalid": "data"})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
```

## Testing Response Models

```python
def test_response_model_serialization(client):
    response = client.get("/api/items/1")
    assert response.status_code == 200
    data = response.json()

    # Verify response model fields
    assert "id" in data
    assert "name" in data
    assert "created_at" in data

    # Verify datetime serialization
    from datetime import datetime
    created_at = datetime.fromisoformat(data["created_at"])
    assert isinstance(created_at, datetime)
```

## Testing Rate Limiting

```python
def test_rate_limit(client):
    for _ in range(10):
        response = client.get("/api/limited/")
        assert response.status_code == 200

    # Next request should be rate limited
    response = client.get("/api/limited/")
    assert response.status_code == 429
```

## Testing CORS

```python
def test_cors_headers(client):
    response = client.options("/api/items/", headers={
        "Origin": "https://example.com",
        "Access-Control-Request-Method": "POST"
    })
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
```

## Testing Pydantic Models

```python
from pydantic import ValidationError

def test_pydantic_model_validation():
    from app.models import ItemCreate

    # Valid data
    item = ItemCreate(name="Test", price=10.0)
    assert item.name == "Test"

    # Invalid data
    with pytest.raises(ValidationError):
        ItemCreate(name="", price=-10)

def test_pydantic_model_serialization():
    from app.models import ItemResponse
    from datetime import datetime

    item = ItemResponse(
        id=1,
        name="Test",
        created_at=datetime.now()
    )

    data = item.model_dump()
    assert "id" in data
    assert "name" in data
```

## Testing Database Operations

```python
@pytest.mark.asyncio
async def test_database_crud(db_session):
    # Create
    item = Item(name="Test", value=100)
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)

    # Read
    retrieved = await db_session.get(Item, item.id)
    assert retrieved.name == "Test"

    # Update
    retrieved.name = "Updated"
    await db_session.commit()

    # Delete
    await db_session.delete(retrieved)
    await db_session.commit()

    result = await db_session.get(Item, item.id)
    assert result is None
```

## Testing Async Endpoints

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/async/")
        assert response.status_code == 200
```

## Common Test Scenarios

```python
# Test query parameters
def test_query_params(client):
    response = client.get("/api/items/?skip=10&limit=5&sort=desc")
    assert response.status_code == 200

# Test path parameters
def test_path_params(client):
    response = client.get("/api/items/123")
    assert response.status_code == 200
    assert response.json()["id"] == 123

# Test request body
def test_request_body(client):
    response = client.post("/api/items/", json={"key": "value"})
    assert response.status_code == 201

# Test headers
def test_custom_headers(client):
    response = client.get("/api/items/", headers={"X-Custom-Header": "value"})
    assert response.status_code == 200

# Test cookies
def test_cookies(client):
    client.cookies.set("session_id", "abc123")
    response = client.get("/api/items/")
    assert response.status_code == 200
```
