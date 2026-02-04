# Python Common Pitfalls

Reference guide for common Python mistakes, security issues, and gotchas.

## Security Vulnerabilities

### SQL Injection

```python
# Bad - SQL injection vulnerability
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)


# Good - use parameterized queries
def get_user(username):
    query = "SELECT * FROM users WHERE username = %s"
    return db.execute(query, (username,))


# Good - use ORM
def get_user(username):
    return User.objects.filter(username=username).first()
```

### Command Injection

```python
# Bad - command injection
import os

def run_command(filename):
    os.system(f"cat {filename}")  # Dangerous!


# Good - use subprocess with list of args
import subprocess

def run_command(filename):
    subprocess.run(['cat', filename], check=True)


# Good - validate input first
import os
from pathlib import Path

def run_command(filename):
    # Validate filename is safe
    safe_path = Path('/safe/directory') / filename
    safe_path = safe_path.resolve()
    if not str(safe_path).startswith('/safe/directory'):
        raise ValueError("Invalid filename")
    subprocess.run(['cat', str(safe_path)], check=True)
```

### Path Traversal

```python
# Bad - path traversal vulnerability
def read_file(filename):
    path = f"/var/app/{filename}"
    with open(path) as f:
        return f.read()
# Input: "../../etc/passwd" -> reads system file!


# Good - validate and sanitize
def read_file(filename):
    safe_dir = Path("/var/app").resolve()
    file_path = (safe_dir / filename).resolve()

    # Ensure result is within safe directory
    if not str(file_path).startswith(str(safe_dir)):
        raise ValueError("Invalid filename")

    with open(file_path) as f:
        return f.read()
```

### Unsafe Deserialization

```python
# Bad - pickle is unsafe
import pickle

def load_data(data):
    return pickle.loads(data)  # Can execute arbitrary code!


# Good - use JSON
import json

def load_data(data):
    return json.loads(data)


# Good - use safe formats (yaml with safe loader)
import yaml

def load_yaml(data):
    return yaml.safe_load(data)  # Not yaml.load()!
```

### Hardcoded Secrets

```python
# Bad - hardcoded secrets
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "password123"
SECRET_KEY = "my-secret-key"


# Good - use environment variables
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")

if not API_KEY:
    raise ValueError("API_KEY must be set")
```

### XSS in Templates

```python
# Bad - manual HTML construction without escaping
def render_html(user_input):
    return f"<div>{user_input}</div>"


# Good - use template engine with auto-escaping
from jinja2 import Template

def render_html(user_input):
    template = Template("<div>{{ user_input }}</div>")
    return template.render(user_input=user_input)


# FastAPI/Django templates auto-escape by default
```

---

## Exception Handling

### Bare Except

```python
# Bad - catches everything including KeyboardInterrupt
try:
    risky_operation()
except:
    pass


# Good - catch specific exceptions
try:
    risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
```

### Swallowing Exceptions

```python
# Bad - exception caught but not handled
try:
    db.save()
except Exception:
    pass  # What went wrong?


# Good - log and handle appropriately
try:
    db.save()
except Exception as e:
    logger.exception("Failed to save to database")
    raise  # Re-raise or handle appropriately
```

### Catching Instead of Finally

```python
# Bad - resource not cleaned up on error
def process_file(filename):
    f = open(filename)
    data = f.read()
    process(data)
    # If process() raises, file never closes!


# Good - use context manager
def process_file(filename):
    with open(filename) as f:
        data = f.read()
    process(data)  # File already closed


# Good - explicit finally if needed
def process_file(filename):
    f = open(filename)
    try:
        data = f.read()
        process(data)
    finally:
        f.close()
```

---

## Resource Management

### Unclosed Files

```python
# Bad - file not closed if error occurs
def read_file(filename):
    f = open(filename)
    return f.read()


# Good - context manager
def read_file(filename):
    with open(filename) as f:
        return f.read()
```

### Unclosed Network Connections

```python
# Bad - connection not closed
def fetch_data(url):
    response = requests.get(url)
    return response.json()


# Good - use context manager
def fetch_data(url):
    with requests.get(url, stream=True) as response:
        return response.json()


# Good - use session with context manager
def fetch_data(url):
    with requests.Session() as session:
        response = session.get(url)
        return response.json()
```

### Database Connections

```python
# Bad - connection not closed
def get_user(user_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()


# Good - use context manager
def get_user(user_id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()
```

---

## Type Safety Issues

### None Handling

```python
# Bad - assuming value is never None
def get_username(user):
    return user.username.upper()  # Crashes if user is None!


# Good - check for None
def get_username(user):
    if user is None:
        return "GUEST"
    return user.username.upper()


# Good - use type hints and handle accordingly
from typing import Optional

def get_username(user: Optional[User]) -> str:
    if user is None:
        return "GUEST"
    return user.username.upper()


# Good - provide default
def get_username(user: Optional[User] = None) -> str:
    return user.username.upper() if user else "GUEST"
```

### Type Mismatch

```python
# Bad - annotation doesn't match usage
def process_items(items: list[str]) -> dict:
    """Returns a list, not dict!"""
    return [item.upper() for item in items]


# Good - matching annotation
def process_items(items: list[str]) -> list[str]:
    """Returns a list."""
    return [item.upper() for item in items]
```

### Missing Type Hints

```python
# Bad - no type hints
def calculate(a, b):
    return a + b


# Good - full type hints
def calculate(a: int, b: int) -> int:
    return a + b


# Good - handle complex types
from typing import list, dict, Optional

def process_data(
    items: list[dict[str, str]],
    limit: Optional[int] = None
) -> dict[str, list[str]]:
    pass
```

---

## Concurrency Issues

### Race Conditions

```python
# Bad - race condition
counter = 0

def increment():
    global counter
    counter += 1  # Not atomic!


# Good - use locks
from threading import Lock

counter = 0
lock = Lock()

def increment():
    global counter
    with lock:
        counter += 1


# Good - use atomic operations
import threading

counter = threading.AtomicCounter(0)
counter.increment()
```

### Deadlock Risk

```python
# Bad - potential deadlock
def transfer_money(account_a, account_b, amount):
    with account_a.lock:
        with account_b.lock:  # May deadlock if called in reverse order
            account_a.balance -= amount
            account_b.balance += amount


# Good - consistent lock ordering
def transfer_money(account_a, account_b, amount):
    # Always lock lower ID first
    first, second = sorted([account_a, account_b], key=lambda x: x.id)
    with first.lock:
        with second.lock:
            account_a.balance -= amount
            account_b.balance += amount
```

### Async with Blocking Calls

```python
# Bad - blocking call in async function
import time

async def fetch_data():
    time.sleep(1)  # Blocks event loop!
    return "data"


# Good - use async version
import asyncio

async def fetch_data():
    await asyncio.sleep(1)  # Non-blocking
    return "data"


# Good - run blocking in thread pool
async def fetch_data():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, blocking_function)
```

---

## Mutable Default Arguments

### The Classic Gotcha

```python
# Bad - mutable default argument
def add_item(item, items=[]):
    """Items list is shared across all calls!"""
    items.append(item)
    return items

add_item(1)  # Returns [1]
add_item(2)  # Returns [1, 2] - not empty!


# Good - use None as default
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

---

## Import Issues

### Circular Imports

```python
# module_a.py
from module_b import func_b  # Can cause issues!

def func_a():
    return func_b()


# module_b.py
from module_a import func_a  # Circular!

def func_b():
    return func_a()


# Solution 1 - import inside function
# module_a.py
def func_a():
    from module_b import func_b
    return func_b()


# Solution 2 - reorganize modules
# Create a shared module with common code
# module_a.py and module_b.py both import from shared
```

### Star Imports

```python
# Bad - star imports pollute namespace
from os import *
from sys import *

# Can't tell where functions come from!


# Good - explicit imports
import os
import sys
from pathlib import Path
```

---

## String Manipulation

### String Concatenation in Loops

```python
# Bad - O(n²) due to string immutability
def build_string(items):
    result = ""
    for item in items:
        result += str(item)  # Creates new string each time!
    return result


# Good - use join
def build_string(items):
    return "".join(str(item) for item in items)


# Good - use list comprehension + join
def build_string(items):
    return "".join([str(item) for item in items])
```

---

## Comparison Gotchas

### Is vs Equals

```python
# Bad - using is for value comparison
a = [1, 2, 3]
b = [1, 2, 3]
if a is b:  # False - different objects!
    print("Same")


# Good - using == for value comparison
if a == b:  # True - same values
    print("Equal")


# Good - using is for None
if value is None:  # Correct
    print("None")

if value is not None:  # Correct
    print("Not None")
```

### Boolean Evaluation

```python
# Gotcha - empty containers are False
items = []
if not items:  # True - empty list is falsy
    print("Empty")


# Gotcha - 0 is False
count = 0
if not count:  # True - 0 is falsy
    print("Zero")


# Good - be explicit when needed
if len(items) == 0:
    print("Empty")

if count == 0:
    print("Zero")
```

---

## List and Dictionary Gotchas

### Modifying List While Iterating

```python
# Bad - modifies list during iteration
items = [1, 2, 3, 4, 5]
for item in items:
    if item % 2 == 0:
        items.remove(item)  # Skips elements!


# Good - create new list
items = [1, 2, 3, 4, 5]
items = [item for item in items if item % 2 != 0]


# Good - iterate over copy
items = [1, 2, 3, 4, 5]
for item in items[:]:
    if item % 2 == 0:
        items.remove(item)
```

### Dictionary Key Modification

```python
# Bad - modifying dict while iterating
data = {'a': 1, 'b': 2, 'c': 3}
for key in data:
    if data[key] == 2:
        del data[key]  # RuntimeError!


# Good - create list of keys first
data = {'a': 1, 'b': 2, 'c': 3}
for key in list(data.keys()):
    if data[key] == 2:
        del data[key]


# Good - dict comprehension
data = {'a': 1, 'b': 2, 'c': 3}
data = {k: v for k, v in data.items() if v != 2}
```

---

## Scope Issues

### Late Binding Closures

```python
# Gotcha - all functions use the same i
funcs = [lambda: i for i in range(3)]
for f in funcs:
    print(f())  # Prints 2, 2, 2 - not 0, 1, 2!


# Solution - capture i in default argument
funcs = [lambda i=i: i for i in range(3)]
for f in funcs:
    print(f())  # Prints 0, 1, 2


# Solution - use functools.partial
from functools import partial

funcs = [partial(lambda x: x, i) for i in range(3)]
```

---

## Copy vs Reference

### Shallow Copy Issues

```python
# Gotcha - shallow copy doesn't copy nested objects
original = [[1, 2], [3, 4]]
shallow = original.copy()  # or list(original)
shallow[0][0] = 999
print(original[0][0])  # 999 - also changed!


# Good - deep copy
import copy

original = [[1, 2], [3, 4]]
deep = copy.deepcopy(original)
deep[0][0] = 999
print(original[0][0])  # 1 - unchanged
```

---

## Integer Division

```python
# Python 2 vs 3 difference
# In Python 3, / always returns float
result = 5 / 2  # 2.5

# For integer division, use //
result = 5 // 2  # 2

# Good to be explicit
result = int(5 / 2)  # 2 - explicit integer conversion
```

---

## Enumerate Gotchas

```python
# Bad - manually tracking index
items = ['a', 'b', 'c']
for i in range(len(items)):
    print(i, items[i])


# Good - use enumerate
for i, item in enumerate(items):
    print(i, item)


# Good - specify start index
for i, item in enumerate(items, start=1):
    print(i, item)  # Starts at 1
```

---

## Performance Issues

### Expensive Operations in Loops

```python
# Bad - regex compilation in loop
import re

items = ['test@example.com', 'invalid', 'user@domain.com']
for email in items:
    if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        print(email)


# Good - compile once
import re

EMAIL_PATTERN = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

for email in items:
    if EMAIL_PATTERN.match(email):
        print(email)


# Good - regex in function (compile once on module load)
import re

EMAIL_PATTERN = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email))
```

### Inefficient Data Structures

```python
# Bad - O(n) lookup in list
items = [1, 2, 3, 4, 5]
for i in range(1000):
    if 3 in items:  # Scans entire list each time
        pass


# Good - O(1) lookup in set
items = {1, 2, 3, 4, 5}
for i in range(1000):
    if 3 in items:  # Constant time lookup
        pass
```

---

## Memory Issues

### Large File Reading

```python
# Bad - reads entire file into memory
def read_file(filename):
    with open(filename) as f:
        return f.readlines()  # All lines in memory!


# Good - process line by line
def read_file(filename):
    with open(filename) as f:
        for line in f:
            process(line)


# Good - use generator
def read_lines(filename):
    with open(filename) as f:
        for line in f:
            yield line
```

---

## Common Framework Issues

### Django - N+1 Query Problem

```python
# Bad - N+1 queries
def get_posts_with_authors():
    posts = Post.objects.all()
    result = []
    for post in posts:
        result.append({
            'title': post.title,
            'author': post.author.username  # Query per post!
        })
    return result


# Good - use select_related
def get_posts_with_authors():
    posts = Post.objects.select_related('author').all()
    return [
        {
            'title': post.title,
            'author': post.author.username  # No extra query!
        }
        for post in posts
    ]
```

### FastAPI - Blocking in Async

```python
# Bad - blocking I/O in async route
@router.get("/posts")
async def get_posts():
    posts = sync_db.query(Post).all()  # Blocks!
    return posts


# Good - use async DB
@router.get("/posts")
async def get_posts():
    result = await async_db.execute(select(Post))
    return result.scalars().all()


# Good - or use sync route
@router.get("/posts")
def get_posts():
    posts = sync_db.query(Post).all()
    return posts
```

---

## Testing Pitfalls

### Testing Implementation Details

```python
# Bad - testing implementation
def test_process_data():
    data = {'items': [1, 2, 3]}
    result = process_data(data)
    assert result['processed'] is True  # Testing internal structure!


# Good - testing behavior
def test_process_data():
    data = {'items': [1, 2, 3]}
    result = process_data(data)
    assert result['total'] == 6  # Tests actual output
```

### Not Mocking External Services

```python
# Bad - makes real API call
def test_get_user():
    user = get_user_from_api(123)  # Real API call!
    assert user.name == "John"


# Good - mock external service
from unittest.mock import patch

@patch('module.requests.get')
def test_get_user(mock_get):
    mock_get.return_value.json.return_value = {'name': 'John'}
    user = get_user_from_api(123)
    assert user.name == "John"
    assert mock_get.called
```
