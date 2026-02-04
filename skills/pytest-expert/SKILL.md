---
name: pytest-expert
description: pytest testing expert for Python projects. Expert in writing unit and integration tests using pytest framework. Specialized in Django and FastAPI testing. Handles test fixtures, mocking external services, and test coverage analysis. Use when: (1) Writing new test cases for Django/FastAPI projects, (2) Analyzing and improving test coverage, (3) Fixing failing tests, (4) Setting up pytest configuration, (5) Creating mock fixtures for external services.
---

# pytest Testing Expert

Expert in writing comprehensive, production-ready tests using pytest for Python projects, with specialization in Django and FastAPI frameworks.

## Quick Start

1. **Identify the project framework** (Django or FastAPI)
2. **Check existing test setup** (`pytest.ini`, `conftest.py`, tests directory)
3. **Write complete, runnable test files**
4. **Verify tests pass** before delivering

---

## Workflow

### Step 1: Understand the Code to Test

Before writing tests, read and understand:
- The code structure (models, views, API endpoints, services)
- Dependencies and external services
- Input/output contracts
- Error scenarios

Use `Read` and `Grep` tools to examine the code.

### Step 2: Choose the Right Reference

Based on project framework:

| Framework | Reference |
|-----------|-----------|
| Django | `references/django.md` |
| FastAPI | `references/fastapi.md` |

For common patterns:
- Fixtures: `references/fixtures.md`
- Mocking: `references/mock.md`
- Coverage: `references/coverage.md`

### Step 3: Use Asset Templates

Copy and customize appropriate templates:

| Template | Purpose |
|----------|---------|
| `assets/pytest.ini` | pytest configuration |
| `assets/conftest_django.py` | Django test fixtures |
| `assets/conftest_fastapi.py` | FastAPI test fixtures |
| `assets/.coveragerc` | Coverage configuration |

### Step 4: Write Complete Test Files

Every test file should be:
- **Immediately runnable** - no placeholders or TODOs
- **Complete** - covers happy path and edge cases
- **Independent** - no test dependencies
- **Clear** - descriptive test names and comments

### Step 5: Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest path/to/test_file.py

# Run with coverage
pytest --cov=. --cov-report=html
```

---

## Django Testing Pattern

### Structure
```python
# tests/test_models.py
import pytest
from myapp.models import MyModel

@pytest.mark.django_db
def test_model_creation():
    obj = MyModel.objects.create(name="test")
    assert obj.name == "test"

# tests/test_views.py
@pytest.mark.django_db
def test_list_view(client):
    response = client.get("/api/endpoint/")
    assert response.status_code == 200
    assert "results" in response.json()

# tests/test_api.py
@pytest.mark.django_db
@patch("myapp.services.external_api_call")
def test_api_with_mock(mock_api, client):
    mock_api.return_value = {"data": "mocked"}
    response = client.post("/api/endpoint/", {"key": "value"})
    assert response.status_code == 201
```

### Key Fixtures
- `client` - Django test client
- `user` / `admin_user` - Test users
- `authenticated_client` - Logged-in client
- `api_client` - DRF API client
- `db` - Database access

---

## FastAPI Testing Pattern

### Structure
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_item(client):
    response = client.post("/api/items/", json={"name": "Test"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test"

# tests/test_auth.py
def test_unauthorized_access(client):
    response = client.get("/api/protected/")
    assert response.status_code == 401

# tests/test_async.py
@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/async/")
        assert response.status_code == 200
```

### Key Fixtures
- `client` - TestClient
- `async_client` - Async HTTP client
- `test_db` - Test database session
- `auth_headers` - Authentication headers
- `authenticated_client` - Client with auth

---

## Mocking External Services

### HTTP Services
```python
@patch("requests.get")
def test_external_api(mock_get, client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value = mock_response

    response = client.get("/api/proxy/")
    assert response.status_code == 200
```

### Google Play / AWS / External APIs
```python
@patch("vps.utils.gp.GooglePlayService.get_token")
def test_vps_endpoint(mock_token, client):
    mock_token.return_value = "fake_token"
    response = client.get("/api/vps/data/")
    assert response.status_code == 200
```

### Database / Cache / Email
```python
@patch("myapp.cache.get")
def test_with_cache_mock(mock_cache):
    mock_cache.return_value = "cached_value"
    result = get_data()
    assert result == "cached_value"
```

---

## Test Coverage Analysis

### Run Coverage
```bash
pytest --cov=. --cov-report=html --cov-report=term-missing
```

### Analyze Results
- Open `htmlcov/index.html` for detailed view
- Check terminal output for missing lines
- Focus on critical paths first

### Improve Coverage
1. Identify uncovered code
2. Write tests for uncovered branches
3. Re-run coverage to verify

---

## Best Practices

### DO
- Write descriptive test names: `test_user_can_login_with_valid_credentials`
- Use fixtures for shared test data
- Mock external services (APIs, databases, cache)
- Test error cases and edge cases
- Keep tests independent and fast
- Use markers (`@pytest.mark.unit`, `@pytest.mark.integration`)

### DON'T
- Don't write tests that depend on execution order
- Don't use placeholders or TODO comments
- Don't test third-party libraries
- Don't write brittle tests that break with minor changes
- Don't forget to mock external services

---

## Output Format

When asked to write tests, always provide:

1. **Complete test files** - no placeholders
2. **Configuration files** if needed (pytest.ini, conftest.py)
3. **Commands to run tests**
4. **Expected results**

Example:
```python
# tests/test_views.py
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_item_list(client):
    url = reverse("api:item-list")
    response = client.get(url)
    assert response.status_code == 200
    assert "results" in response.json()
```

---

## Common Commands

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_views.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Run parallel (requires pytest-xdist)
pytest -n auto
```
