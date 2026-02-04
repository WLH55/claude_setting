# Django Best Practices

Reference guide for reviewing Django code. Based on [zh-django-best-practices](https://github.com/yangyubo/zh-django-best-practices).

## Project Structure

### Recommended Layout

```
project/
├── README.md
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── docs/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   └── base.html
├── logs/
└── config/
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

### Application Structure

Each Django app should be a reusable, focused module:

```
app_name/
├── __init__.py
├── admin.py          # Admin configuration (MODELAdmin naming)
├── apps.py           # App configuration
├── forms.py          # Form classes
├── managers.py       # Custom model managers
├── middleware.py     # Middleware (minimal tasks)
├── models.py         # Database models (or models/ directory)
├── signals.py        # Signal handlers
├── templates/
│   └── app_name/     # App-specific templates
│       └── template.html
├── templatetags/
│   └── app_name_tags.py
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── urls.py           # URL patterns with name attributes
└── views.py          # Views (or views/ directory)
```

### What is a Reusable App?

- Focused on a single functionality
- Follows Unix philosophy: "do one thing well"
- Can be easily embedded in any project
- Has clear, minimal dependencies

---

## Code Style

### PEP 8 Compliance

```python
# Good
def get_user_profile(user_id):
    """Get user profile by ID."""
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


# Bad - function name should be snake_case
def getUserProfile(userId):
    return User.objects.get(id=userId)
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Models | PascalCase | `UserProfile`, `BlogPost` |
| Functions | snake_case | `get_user()`, `calculate_total()` |
| Variables | snake_case | `user_id`, `total_amount` |
| Constants | UPPER_CASE | `MAX_RETRIES`, `API_KEY` |
| Classes | PascalCase | `UserSerializer`, `LoginView` |

### Admin Configuration

```python
# Good - MODELAdmin naming
from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'


# Bad - unclear naming
class CustomAdmin(admin.ModelAdmin):
    pass
```

---

## Model Best Practices

### Model Definition

```python
# Good
from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    """Blog post model."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    content = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:post-detail', kwargs={'slug': self.slug})
```

### Common Model Issues to Check

#### Issue 1: Missing related_name

```python
# Bad - no related_name
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


# Good - explicit related_name
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
```

#### Issue 2: Not using indexes

```python
# Bad - fields used in queries without indexes
class Post(models.Model):
    title = models.CharField(max_length=200)
    published_date = models.DateTimeField()


# Good - indexed fields
class Post(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    published_date = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['published_date']),
        ]
```

#### Issue 3: Business logic in views instead of models

```python
# Bad - logic in view
def publish_post(request, post_id):
    post = Post.objects.get(id=post_id)
    post.status = 'published'
    post.published_date = timezone.now()
    post.save()
    return redirect('post-detail', post_id=post.id)


# Good - logic in model
class Post(models.Model):
    # ... fields ...

    def publish(self):
        """Publish the post."""
        self.status = 'published'
        self.published_date = timezone.now()
        self.save()


def publish_post(request, post_id):
    post = Post.objects.get(id=post_id)
    post.publish()
    return redirect('post-detail', post_id=post.id)
```

---

## View Best Practices

### Keep Views Thin

```python
# Bad - too much logic in view
def post_list(request):
    posts = Post.objects.filter(status='published')
    for post in posts:
        post.comment_count = post.comments.count()
        post.author_name = post.author.username
    categories = Category.objects.all()
    for cat in categories:
        cat.post_count = cat.posts.count()
    context = {'posts': posts, 'categories': categories}
    return render(request, 'blog/post_list.html', context)


# Good - logic in services/managers
def post_list(request):
    posts = Post.objects.published().with_comment_count()
    categories = Category.objects.with_post_count()
    context = {'posts': posts, 'categories': categories}
    return render(request, 'blog/post_list.html', context)
```

### Use Proper HTTP Methods

```python
# Good
from django.views.decorators.http import require_http_methods


@require_http_methods(['GET', 'POST'])
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post-list')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})
```

### Class-Based Views vs Function Views

```python
# Use Class-Based Views for CRUD
from django.views.generic import ListView, DetailView, CreateView


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/post_list.html'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.published()


# Use Function Views for custom logic
def custom_report(request):
    # Complex custom logic
    data = generate_complex_report()
    return render(request, 'report.html', {'data': data})
```

---

## URL Configuration

### Always Use Name Parameter

```python
# Good
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post-list'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/create/', views.post_create, name='post-create'),
]


# Usage in templates
<a href="{% url 'blog:post-detail' slug=post.slug %}">{{ post.title }}</a>

# Usage in views
from django.urls import reverse
return redirect(reverse('blog:post-detail', kwargs={'slug': post.slug}))
```

### URL Naming Convention

Use format: `app_model_action` or `app:model-action`

```python
# Examples
'blog:post-list'        # List posts
'blog:post-detail'      # Single post
'blog:post-create'      # Create post
'blog:post-update'      # Update post
'blog:post-delete'      # Delete post
'user:profile-detail'   # User profile
'user:profile-update'   # Update profile
```

---

## Template Best Practices

### Standard Block Names

```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Site{% endblock %}</title>
    {% block extra_head %}{% endblock %}
</head>
<body class="{% block body_class %}{% endblock %}">
    {% block header %}{% endblock %}

    {% block menu %}{% endblock %}

    <main>
        {% block content %}{% endblock %}
    </main>

    {% block footer %}{% endblock %}
</body>
</html>
```

### Template Organization

```
templates/
├── base.html
├── app_name/
│   ├── base.html           # App-specific base
│   ├── model_list.html
│   ├── model_detail.html
│   └── model_form.html
└── registration/
    ├── login.html
    └── register.html
```

---

## Settings and Configuration

### Use Environment Variables

```python
# Good
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
DATABASE_URL = os.getenv('DATABASE_URL')


# Bad - hardcoded secrets
SECRET_KEY = 'django-insecure-abc123...'
DEBUG = True
```

### Split Settings by Environment

```
config/
├── __init__.py
├── base.py          # Common settings
├── development.py   # Dev settings
├── production.py    # Prod settings
└── test.py          # Test settings
```

```python
# manage.py
#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)
```

---

## ORM Best Practices

### Avoid N+1 Queries

```python
# Bad - N+1 query problem
def get_posts_with_authors():
    posts = Post.objects.all()
    for post in posts:
        print(post.title, post.author.username)  # Separate query for each author


# Good - use select_related
def get_posts_with_authors():
    posts = Post.objects.select_related('author').all()
    for post in posts:
        print(post.title, post.author.username)  # No additional queries


# Good - use prefetch_related for many-to-many
def get_posts_with_tags():
    posts = Post.objects.prefetch_related('tags').all()
    for post in posts:
        for tag in post.tags.all():  # No additional queries
            print(tag.name)
```

### QuerySet Evaluation

```python
# Good - lazy evaluation
posts = Post.objects.filter(status='published')  # No query yet
posts = posts.filter(category__name='Tech')      # Still no query
for post in posts:                               # Query executes here
    print(post.title)


# Good - explicit evaluation when needed
posts = list(Post.objects.all())  # Force evaluation
```

### Use QuerySet Methods Efficiently

```python
# Bad
ids = [post.id for post in Post.objects.all()]
filtered_posts = Post.objects.filter(id__in=ids)


# Good
filtered_posts = Post.objects.all()
```

---

## Security Best Practices

### CSRF Protection

```python
# Always use csrf_token in forms
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>


# For API views that need to exempt CSRF
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def my_api_view(request):
    pass
```

### SQL Injection Prevention

```python
# Good - use ORM filters (automatically escaped)
Post.objects.filter(title=user_input)


# Bad - never use raw SQL with user input without escaping
cursor.execute(f"SELECT * FROM blog_post WHERE title = '{user_input}'")


# If you must use raw SQL, use params
cursor.execute("SELECT * FROM blog_post WHERE title = %s", [user_input])
```

### XSS Prevention

```python
# Templates auto-escape by default
{{ user_input }}  # Escaped HTML

# Only use |safe with trusted content
{{ trusted_html|safe }}
```

---

## Common Issues to Check

### 1. Missing Migration Files

Check if `models.py` changes have corresponding migrations.

### 2. Hardcoded URLs

```python
# Bad
return redirect('/blog/posts/1/')

# Good
return redirect('blog:post-detail', pk=1)
```

### 3. Missing Error Handling

```python
# Good
from django.shortcuts import get_object_or_404

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})
```

### 4. Not Using Signals Properly

```python
# Good - signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when user is created."""
    if created:
        Profile.objects.create(user=instance)


# apps.py
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals
```

---

## Testing Best Practices

```python
# tests/test_models.py
from django.test import TestCase
from .models import Post


class PostModelTest(TestCase):
    def setUp(self):
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content'
        )

    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertTrue(self.post.published_date)

    def test_post_str_method(self):
        self.assertEqual(str(self.post), 'Test Post')


# tests/test_views.py
from django.test import Client
from django.urls import reverse


class PostViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            status='published'
        )

    def test_post_list_view(self):
        url = reverse('blog:post-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
```
