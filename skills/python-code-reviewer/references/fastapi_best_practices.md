# FastAPI Best Practices

Reference guide for reviewing FastAPI code. Based on [fastapi-best-practices-zh-cn](https://github.com/hellowac/fastapi-best-practices-zh-cn).

## Project Structure

### Domain-Based Structure (Recommended)

```
fastapi-project/
├── alembic/                     # Database migrations
├── src/
│   ├── auth/                    # Auth domain
│   │   ├── router.py            # Routes
│   │   ├── schemas.py           # Pydantic models
│   │   ├── models.py            # DB models
│   │   ├── dependencies.py      # Dependencies
│   │   ├── config.py            # Local config
│   │   ├── constants.py         # Constants and error codes
│   │   ├── exceptions.py        # Custom exceptions
│   │   ├── service.py           # Business logic
│   │   └── utils.py             # Utilities
│   ├── posts/                   # Posts domain
│   │   └── (same structure as auth)
│   ├── users/                   # Users domain
│   │   └── (same structure as auth)
│   ├── config.py                # Global config
│   ├── models.py                # Global models
│   ├── exceptions.py            # Global exceptions
│   ├── database.py              # DB connection
│   └── main.py                  # App entry point
├── tests/
│   ├── auth/
│   ├── posts/
│   └── conftest.py
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── .env
├── .gitignore
└── alembic.ini
```

### Key Principles

- **Consistent structure**: Each domain has the same file layout
- **Predictable**: Know where to find things without opening files
- **Independent**: Domains can be extracted to separate services if needed

---

## Pydantic for Data Validation

### Excessive Use of Pydantic

```python
# Good - comprehensive validation
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator


class MusicBand(str, Enum):
    AEROSMITH = "AEROSMITH"
    QUEEN = "QUEEN"
    ACDC = "AC/DC"


class UserBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=128)
    username: str = Field(pattern=r"^[A-Za-z0-9-_]+$", min_length=3)
    email: EmailStr
    age: int = Field(default=None, ge=18, le=120)
    favorite_band: MusicBand | None = None
    website: str | None = None

    @field_validator('username')
    @classmethod
    def username_to_lowercase(cls, v: str) -> str:
        return v.lower()


# Bad - minimal validation
class UserBase(BaseModel):
    first_name: str
    username: str
    email: str
    age: int = None
```

### Custom Base Model

```python
# Good - custom base model from day 0
from datetime import datetime
from zoneinfo import ZoneInfo
import orjson
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, model_validator


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


def convert_datetime_to_gmt(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class ORJSONModel(BaseModel):
    model_config = ConfigDict(
        json_loads=orjson.loads,
        json_dumps=orjson_dumps,
        json_encoders={datetime: convert_datetime_to_gmt},
    )

    @model_validator(mode='before')
    @classmethod
    def set_null_microseconds(cls, data: dict) -> dict:
        """Drops microseconds in all datetime field values."""
        datetime_fields = {
            k: v.replace(microsecond=0)
            for k, v in data.items()
            if isinstance(v, datetime)
        }
        return {**data, **datetime_fields}

    def serializable_dict(self, **kwargs):
        """Return a dict which contains only serializable fields."""
        default_dict = self.model_dump(**kwargs)
        return jsonable_encoder(default_dict)
```

---

## Dependency Injection

### Use Dependencies for Data Validation

```python
# Good - validate data against DB in dependencies
from fastapi import Depends, HTTPException
from pydantic import UUID4
from sqlalchemy import select
from .models import Post
from .database import async_session


async def get_db():
    async with async_session() as session:
        yield session


async def valid_post_id(post_id: UUID4, db: AsyncSession = Depends(get_db)) -> Post:
    """Validate post exists and return it."""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post_by_id(post: Post = Depends(valid_post_id)):
    return post


@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    update_data: PostUpdate,
    post: Post = Depends(valid_post_id),
    db: AsyncSession = Depends(get_db),
):
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(post, key, value)
    await db.commit()
    await db.refresh(post)
    return post
```

### Chain Dependencies

```python
# Good - dependencies can use other dependencies
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def parse_jwt_data(token: str = Depends(oauth2_scheme)) -> dict:
    """Parse JWT token and return user data."""
    try:
        payload = jwt.decode(token, "JWT_SECRET", algorithms=["HS256"])
        return {"user_id": payload["id"]}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


async def valid_post_id(post_id: UUID4, db: AsyncSession = Depends(get_db)) -> Post:
    """Validate post exists."""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


async def valid_owned_post(
    post: Post = Depends(valid_post_id),
    token_data: dict = Depends(parse_jwt_data),
) -> Post:
    """Validate post exists and user owns it."""
    if post.owner_id != token_data["user_id"]:
        raise HTTPException(status_code=403, detail="Not the owner")
    return post


@router.get("/users/me/posts/{post_id}", response_model=PostResponse)
async def get_user_post(post: Post = Depends(valid_owned_post)):
    return post
```

### Dependency Calls are Cached

```python
# Good - dependencies are cached per request
@router.get("/posts/{post_id}/comments")
async def get_post_comments(
    post: Post = Depends(valid_post_id),
    token_data: dict = Depends(parse_jwt_data),
    user: User = Depends(get_current_user),
):
    # parse_jwt_data is called only once, even though it's used by both
    # valid_owned_post and get_current_user
    return {"post": post, "user": user}
```

---

## RESTful API Design

### Follow REST Conventions

```python
# Good - RESTful design
@router.get("/posts", response_model=list[PostResponse])
async def list_posts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all posts."""
    pass


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post: Post = Depends(valid_post_id)):
    """Get single post."""
    pass


@router.post("/posts", response_model=PostResponse, status_code=201)
async def create_post(
    data: PostCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create new post."""
    pass


@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    data: PostUpdate,
    post: Post = Depends(valid_post_id),
    db: AsyncSession = Depends(get_db),
):
    """Update post."""
    pass


@router.delete("/posts/{post_id}", status_code=204)
async def delete_post(
    post: Post = Depends(valid_post_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete post."""
    pass
```

### Use /me for Current User Resources

```python
# Good - /me endpoints
@router.get("/users/me", response_model=UserResponse)
async def get_current_user(user: User = Depends(get_current_user)):
    return user


@router.get("/users/me/posts", response_model=list[PostResponse])
async def get_my_posts(user: User = Depends(get_current_user)):
    return user.posts


# No need to validate user exists - already checked in auth dependency
# No need to check ownership - it's the current user
```

---

## Async vs Sync

### Don't Make Routes Async for Blocking I/O

```python
# Bad - blocking I/O in async route
import time

@router.get("/ping")
async def terrible_ping():
    time.sleep(10)  # Blocks event loop for 10 seconds!
    return {"pong": "pong"}


# Good - use sync for blocking operations
@router.get("/ping")
def good_ping():
    time.sleep(10)  # Runs in thread pool
    return {"pong": "pong"}


# Good - use async for non-blocking operations
import asyncio

@router.get("/ping")
async def perfect_ping():
    await asyncio.sleep(10)  # Non-blocking
    return {"pong": "pong"}
```

### Rule of Thumb

| Operation Type | Route Type | Reason |
|----------------|------------|--------|
| Async I/O (aiohttp, asyncpg) | `async def` | Non-blocking |
| Blocking I/O (requests, sync DB) | `def` | Runs in thread pool |
| CPU-intensive | `def` + separate process | GIL limitation |

### Run Sync SDK in Thread Pool

```python
# Good - run sync library in thread pool
from fastapi.concurrency import run_in_threadpool
from my_sync_library import SyncAPIClient


@router.get("/external")
async def call_sync_library():
    my_data = await service.get_my_data()
    client = SyncAPIClient()
    result = await run_in_threadpool(client.make_request, data=my_data)
    return result
```

---

## Configuration

### Use Pydantic BaseSettings

```python
# Good - BaseSettings for configuration
from pydantic import BaseSettings, PostgresDsn, AnyUrl, Field


class AppSettings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: PostgresDsn

    # API
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = Field(..., min_length=32)

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # Environment
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = AppSettings()


# Usage
SECRET_KEY = settings.SECRET_KEY
DATABASE_URL = settings.DATABASE_URL
```

### Hide Docs in Production

```python
# Good - conditionally hide docs
from fastapi import FastAPI
from starlette.config import Config

config = Config(".env")
ENVIRONMENT = config("ENVIRONMENT", default="development")
SHOW_DOCS_ENVIRONMENT = ("local", "staging", "development")

app_configs = {"title": "My API"}

if ENVIRONMENT not in SHOW_DOCS_ENVIRONMENT:
    app_configs["openapi_url"] = None

app = FastAPI(**app_configs)
```

---

## Documentation

### Help FastAPI Generate Good Docs

```python
# Good - comprehensive documentation
from fastapi import APIRouter, status

router = APIRouter()


@router.post(
    "/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new blog post. Returns the created post with ID.",
    summary="Create a new post",
    tags=["Posts"],
    responses={
        status.HTTP_201_CREATED: {
            "model": PostResponse,
            "description": "Post created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid input data",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication required",
        },
    },
)
async def create_post(data: PostCreate):
    """Create a new blog post."""
    pass
```

---

## SQLAlchemy Best Practices

### Set DB Naming Convention

```python
# Good - explicit naming convention
from sqlalchemy import MetaData

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)
```

### SQL-First, Pydantic-Second

```python
# Good - do aggregation in DB
from sqlalchemy import func, select, text


async def get_posts_with_creator(db: AsyncSession) -> list[dict]:
    """Get posts with creator info aggregated in DB."""
    query = (
        select(
            posts.c.id,
            posts.c.title,
            func.json_build_object(
                text("'id'", profiles.c.id),
                text("'username'", profiles.c.username),
            ).label("creator"),
        )
        .select_from(posts.join(profiles, posts.c.owner_id == profiles.c.id))
        .order_by(posts.c.created_at.desc())
    )
    return await db.execute(query)


# Schema with JSON parser
from pydantic import BaseModel, field_validator


class Creator(BaseModel):
    id: UUID4
    username: str


class Post(BaseModel):
    id: UUID4
    title: str
    creator: Creator  # Parsed from JSON

    @field_validator('creator', mode='before')
    @classmethod
    def parse_creator_json(cls, v: str | dict | Creator) -> dict | Creator:
        if isinstance(v, str):
            return orjson.loads(v)
        return v
```

---

## Type Hints

### Typing is Important

```python
# Bad - no type hints
def get_posts(skip, limit):
    return posts[skip:skip+limit]


# Good - full type hints
from typing import list

def get_posts(skip: int, limit: int) -> list[Post]:
    return posts[skip:skip+limit]
```

---

## File Upload

### Save Files in Chunks

```python
# Good - save in chunks
import aiofiles
from fastapi import UploadFile

DEFAULT_CHUNK_SIZE = 1024 * 1024 * 50  # 50 MB


async def save_video(video_file: UploadFile, file_path: str):
    """Save video file in chunks."""
    async with aiofiles.open(file_path, "wb") as f:
        while chunk := await video_file.read(DEFAULT_CHUNK_SIZE):
            await f.write(chunk)
```

---

## Dynamic Pydantic Fields

### Be Careful with Union Types

```python
# Bad - ambiguous union
class Article(BaseModel):
    text: str | None
    extra: str | None


class Video(BaseModel):
    video_id: int
    text: str | None
    extra: str | None


class Post(BaseModel):
    content: Article | Video


# Problem: Any dict becomes valid Article
post = Post(content={"video_id": 1, "text": "text"})
print(type(post.content))  # Output: Article (wrong!)


# Solution 1: forbid extra fields
class Article(BaseModel):
    text: str | None
    extra: str | None

    model_config = ConfigDict(extra='forbid')


class Video(BaseModel):
    video_id: int
    text: str | None
    extra: str | None

    model_config = ConfigDict(extra='forbid')


# Solution 2: order by strictness (most strict first)
class Post(BaseModel):
    content: Video | Article  # Video first!
```

---

## Custom Validators

### Raise ValueError for Client-Facing Schemas

```python
# Good - ValueError returns nice error to client
from pydantic import field_validator


class ProfileCreate(BaseModel):
    username: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if v == "me":
            raise ValueError("Username 'me' is reserved")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v


# Bad - HTTPException in validator
class ProfileCreate(BaseModel):
    username: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if v == "me":
            raise HTTPException(  # Don't do this!
                status_code=400,
                detail="Username 'me' is reserved"
            )
        return v
```

---

## URL Validation

### Validate Hosts for User URLs

```python
# Good - whitelist allowed hosts
from pydantic import AnyUrl, BaseModel

ALLOWED_MEDIA_URLS = {"mysite.com", "mysite.org"}


class CompanyMediaUrl(AnyUrl):
    """URL that only allows whitelisted hosts."""

    @classmethod
    def validate_host(cls, parts: dict) -> tuple[str, str, str, bool]:
        host, tld, host_type, rebuild = super().validate_host(parts)
        if host not in ALLOWED_MEDIA_URLS:
            raise ValueError(
                f"Forbidden host URL. Only {ALLOWED_MEDIA_URLS} allowed"
            )
        return host, tld, host_type, rebuild


class Profile(BaseModel):
    avatar_url: CompanyMediaUrl  # Only whitelisted URLs


# Usage
profile = Profile(avatar_url="https://mysite.com/avatar.png")  # OK
profile = Profile(avatar_url="https://evil.com/avatar.png")    # Error!
```

---

## Background Tasks

### Use BackgroundTasks Over asyncio.create_task

```python
# Good - BackgroundTasks for both sync and async
from fastapi import BackgroundTasks


@router.post("/users/{user_id}/email")
async def send_user_email(
    user_id: UUID4,
    background_tasks: BackgroundTasks,
):
    """Send email to user."""
    background_tasks.add_task(notifications_service.send_email, user_id)
    return {"status": "ok"}


# Bad - asyncio.create_task
@router.post("/users/{user_id}/email")
async def send_user_email(user_id: UUID4):
    """Don't do this!"""
    asyncio.create_task(notifications_service.send_email(user_id))
    return {"status": "ok"}
```

---

## Common Issues to Check

### 1. Missing Response Model

```python
# Bad - no response_model
@router.get("/posts/{post_id}")
async def get_post(post_id: UUID4):
    return post


# Good - explicit response model
@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: UUID4):
    return post
```

### 2. Not Using Dependencies

```python
# Bad - validation in route
@router.get("/posts/{post_id}")
async def get_post(post_id: UUID4, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404)
    return post


# Good - validation in dependency
@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post: Post = Depends(valid_post_id)):
    return post
```

### 3. Not Chaining Dependencies

```python
# Bad - duplicate validation
@router.get("/posts/{post_id}")
async def get_post(
    post_id: UUID4,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    # Validate post exists
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(404)

    # Validate ownership
    payload = jwt.decode(token, "SECRET", algorithms=["HS256"])
    if post.owner_id != payload["id"]:
        raise HTTPException(403)

    return post


# Good - chained dependencies
@router.get("/posts/{post_id}")
async def get_post(
    post: Post = Depends(valid_owned_post),
):
    return post
```

### 4. Sync DB in Async Route

```python
# Bad - sync DB operations in async route
@router.get("/posts")
async def get_posts(db: Session = Depends(get_sync_db)):
    return db.query(Post).all()


# Good - async DB operations
@router.get("/posts")
async def get_posts(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Post))
    return result.scalars().all()
```

---

## Testing Best Practices

### Use Async Test Client from Day 0

```python
# conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from main import app


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# tests/test_posts.py
@pytest.mark.asyncio
async def test_create_post(client: AsyncClient):
    response = await client.post(
        "/posts",
        json={"title": "Test", "content": "Content"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test"
```

---

## Linting

### Use Pre-Commit Hooks

```bash
# pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/myint/autoflake
    rev: v2.0.0
    hooks:
      - id: autoflake
        args: [
          "--remove-all-unused-imports",
          "--remove-unused-variables",
          "--in-place"
        ]
```

### Linter Script

```bash
#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive \
    --remove-unused-variables --in-place src tests --exclude=__init__.py
isort src tests --profile black
black src tests
mypy src
```
