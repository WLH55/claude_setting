# Django Testing with pytest

## Test Structure

```python
# tests/test_models.py
@pytest.mark.django_db
def test_model_creation():
    obj = MyModel.objects.create(name="test")
    assert obj.name == "test"

# tests/test_views.py
@pytest.mark.django_db
def test_list_view(client):
    response = client.get("/api/endpoint/")
    assert response.status_code == 200
    assert response.json()["count"] == 1

# tests/test_forms.py
@pytest.mark.django_db
def test_form_valid():
    form = MyForm(data={"name": "valid"})
    assert form.is_valid()

# tests/test_api.py
@pytest.mark.django_db
@patch("module.external_service_call")
def test_api_with_mock(mock_service, client):
    mock_service.return_value = {"data": "mocked"}
    response = client.post("/api/endpoint/", {"key": "value"})
    assert response.status_code == 201
```

## Django Fixtures

```python
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="admin123"
    )

@pytest.fixture
def authenticated_client(client, user):
    client.force_login(user)
    return client

@pytest.fixture
def api_client(client):
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {get_token()}"
    return client
```

## Testing Django ORM

```python
@pytest.mark.django_db
def test_queryset_filters():
    MyModel.objects.create(category="A", status="active")
    MyModel.objects.create(category="B", status="active")

    active = MyModel.objects.filter(status="active")
    assert active.count() == 2

    category_a = MyModel.objects.filter(category="A")
    assert category_a.exists()

@pytest.mark.django_db
def test_related_objects():
    author = Author.objects.create(name="Test Author")
    book = Book.objects.create(title="Test Book", author=author)

    assert author.books.count() == 1
    assert book.author == author
```

## Testing Views with Client

```python
from django.urls import reverse

@pytest.mark.django_db
def test_list_view(client):
    url = reverse("myapp:list")
    response = client.get(url)

    assert response.status_code == 200
    assert "items" in response.json()

@pytest.mark.django_db
def test_detail_view(client, obj):
    url = reverse("myapp:detail", kwargs={"pk": obj.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert response.json()["id"] == obj.pk

@pytest.mark.django_db
def test_create_view(client):
    response = client.post("/api/create/", {
        "name": "New Item",
        "value": 100
    }, content_type="application/json")

    assert response.status_code == 201
    assert MyModel.objects.filter(name="New Item").exists()

@pytest.mark.django_db
def test_view_permissions(authenticated_client):
    response = authenticated_client.get("/protected/")
    assert response.status_code == 200

def test_view_requires_login(client):
    response = client.get("/protected/")
    assert response.status_code == 302  # Redirect to login
```

## Testing Django Forms

```python
@pytest.mark.django_db
def test_form_with_valid_data():
    form = MyForm({
        "name": "Test",
        "email": "test@example.com"
    })
    assert form.is_valid()

@pytest.mark.django_db
def test_form_with_invalid_data():
    form = MyForm({
        "name": "",
        "email": "invalid"
    })
    assert not form.is_valid()
    assert "name" in form.errors

@pytest.mark.django_db
def test_form_save():
    form = MyForm({"name": "Test"})
    if form.is_valid():
        obj = form.save()
        assert obj.name == "Test"
```

## Testing Management Commands

```python
from io import StringIO
from django.core.management import call_command

@pytest.mark.django_db
def test_my_command():
    out = StringIO()
    call_command('my_command', stdout=out)
    assert "Success" in out.getvalue()

@pytest.mark.django_db
def test_command_with_arguments():
    out = StringIO()
    call_command('my_command', '--option=value', stdout=out)
    assert "value" in out.getvalue()
```

## Testing Signals

```python
import pytest
from django.db.models.signals import post_save
from apps.myapp.models import MyModel

@pytest.mark.django_db
def test_signal_fired():
    with pytest.signal_receiver(post_save, sender=MyModel) as receiver:
        obj = MyModel.objects.create(name="test")
        assert receiver.called
```

## Testing Middleware

```python
@pytest.mark.django_db
def test_middleware_adds_header(client):
    response = client.get("/api/test/")
    assert "X-Custom-Header" in response
```

## Testing Django REST Framework

```python
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_api_endpoint(api_client):
    response = api_client.get("/api/v1/items/")
    assert response.status_code == 200
    assert response.json()["count"] >= 0

@pytest.mark.django_db
def test_api_authentication_required(api_client):
    response = api_client.post("/api/v1/items/", {})
    assert response.status_code == 401

@pytest.mark.django_db
def test_api_with_token(api_client, token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.post("/api/v1/items/", {"name": "test"})
    assert response.status_code == 201
```

## Testing File Uploads

```python
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.mark.django_db
def test_file_upload(client):
    file = SimpleUploadedFile(
        "test.txt",
        b"file content",
        content_type="text/plain"
    )
    response = client.post("/upload/", {"file": file})
    assert response.status_code == 201
```

## Testing Email Sending

```python
from django.core import mail
from django.test import override_settings

@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
def test_email_sent():
    # Trigger email sending
    send_notification()

    assert len(mail.outbox) == 1
    assert "Subject" in mail.outbox[0].subject
    assert "recipient@example.com" in mail.outbox[0].to
```

## Testing Pagination

```python
@pytest.mark.django_db
def test_pagination(client):
    # Create 25 items
    for i in range(25):
        MyModel.objects.create(name=f"Item {i}")

    response = client.get("/api/items/?page=1&page_size=10")
    data = response.json()

    assert data["count"] == 25
    assert len(data["results"]) == 10
    assert data["next"] is not None
```

## Testing Filters

```python
@pytest.mark.django_db
def test_filter_by_category(client):
    MyModel.objects.create(category="A", name="Item 1")
    MyModel.objects.create(category="B", name="Item 2")

    response = client.get("/api/items/?category=A")
    data = response.json()

    assert len(data["results"]) == 1
    assert data["results"][0]["category"] == "A"
```

## Testing Permissions

```python
from django.contrib.auth.models import Permission

@pytest.mark.django_db
def test_user_with_permission(authenticated_client, user):
    permission = Permission.objects.get(codename="add_model")
    user.user_permissions.add(permission)

    response = authenticated_client.post("/api/items/", {"name": "test"})
    assert response.status_code == 201

@pytest.mark.django_db
def test_user_without_permission(authenticated_client):
    response = authenticated_client.post("/api/items/", {"name": "test"})
    assert response.status_code == 403
```

## Common pytest-django Marks

```python
# Mark tests that need database access
@pytest.mark.django_db

# Mark tests that need database and reset database after
@pytest.mark.django_db_reset_sequences

# Mark tests that should not access database
@pytest.mark.no_db

# Mark tests as integration tests
@pytest.mark.integration

# Run only marked tests: pytest -m integration
# Skip marked tests: pytest -m "not integration"
```
