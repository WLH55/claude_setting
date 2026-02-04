# Test Coverage with pytest

## Installation

```bash
# Install pytest-cov
uv add pytest pytest-cov
```

## Basic Coverage Configuration

### pytest.ini
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.dev
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-report=xml
    -v
```

### pyproject.toml
```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.dev"
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--cov=.",
    "--cov-report=html",
    "--cov-report=term-missing",
    "-v"
]

[tool.coverage.run]
source = ["."]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/venv/*",
    "*/env/*",
    "manage.py",
    "*/settings/*",
    "*/wsgi.py",
    "*/asgi.py",
    "*/conftest.py"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod"
]
```

## Running Coverage

```bash
# Run with coverage
pytest --cov=. --cov-report=html

# Run coverage for specific app
pytest --cov=myapp --cov-report=html

# Run coverage with terminal report
pytest --cov=. --cov-report=term-missing

# Generate XML report (for CI/CD)
pytest --cov=. --cov-report=xml

# Combine coverage from multiple runs
pytest --cov=. --cov-append
pytest --cov=another_app --cov-append

# Report with missing lines
pytest --cov=. --cov-report=term-missing:skip-covered

# Minimum coverage percentage (fail if below)
pytest --cov=. --cov-fail-under=80
```

## Coverage Reports

### HTML Report
```bash
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

### Terminal Report
```bash
# Simple terminal report
pytest --cov=. --cov-report=term

# Show missing lines
pytest --cov=. --cov-report=term-missing

# Skip covered files
pytest --cov=. --cov-report=term-missing:skip-covered
```

### XML Report
```bash
# For CI tools (Codecov, Coveralls, etc.)
pytest --cov=. --cov-report=xml:coverage.xml
```

### JSON Report
```bash
# For custom processing
pytest --cov=. --cov-report=json:coverage.json
```

## Coverage Configuration

### Omit Files/Directories

```ini
# In .coveragerc or pyproject.toml
[run]
omit =
    */tests/*
    */test_*.py
    */migrations/*
    */venv/*
    */env/*
    manage.py
    */settings/*
    */wsgi.py
    */asgi.py
    */conftest.py
    */__pycache__/*
    */site-packages/*
```

### Branch Coverage

```ini
[run]
branch = True

[report]
show_missing = True
precision = 2
```

### Exclude Lines

```ini
[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod
    @abstractproperty
```

## Common Patterns

### Per-Application Coverage

```bash
# Coverage for specific app
pytest myapp/tests/ --cov=myapp --cov-report=html

# Coverage for multiple apps
pytest --cov=myapp --cov=another_app --cov-report=html
```

### Coverage with Parallel Tests

```bash
# With pytest-xdist
pytest -n auto --cov=. --cov-append
```

### Minimum Coverage Threshold

```bash
# Fail if coverage below 80%
pytest --cov=. --cov-fail-under=80

# In pytest.ini
addopts = --cov=. --cov-fail-under=80
```

### Combining Coverage from Multiple Runs

```bash
# Run tests in stages, combining coverage
pytest tests/test_models/ --cov=. --cov-append
pytest tests/test_views/ --cov=. --cov-append
pytest tests/test_api/ --cov=. --cov-append
# Then generate report
coverage report
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-django

      - name: Run tests with coverage
        run: |
          pytest --cov=. --cov-report=xml --cov-report=term-missing

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### GitLab CI

```yaml
test:
  stage: test
  script:
    - pip install pytest pytest-cov
    - pytest --cov=. --cov-report=xml --cov-report=term
  coverage: '/(?i)total.*? (100(?:\.0+)?\%|[1-9]?\d(?:\.\d+)?\%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## Coverage for Django Projects

### Configuration

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.dev
addopts =
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-config=.coveragerc

[run]
source = .
omit =
    */tests/*
    */migrations/*
    */settings/*
    manage.py
    */wsgi.py
    */asgi.py
```

### Test Commands

```bash
# Run all tests with coverage
pytest --cov=. --cov-report=html

# Run specific app tests
pytest myapp/tests/ --cov=myapp --cov-report=html

# Run with coverage for apps only
pytest --cov=myapp --cov=another_app --cov-report=html
```

## Coverage for FastAPI Projects

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts =
    --cov=app
    --cov-report=html
    --cov-report=term-missing
```

## Debugging Low Coverage

### Find Uncovered Lines

```bash
# Show missing lines in terminal
pytest --cov=. --cov-report=term-missing

# Generate HTML report for detailed view
pytest --cov=. --cov-report=html
# Open htmlcov/index.html
```

### Coverage by Module

```bash
# Check specific module coverage
pytest --cov=myapp.models --cov-report=term-missing

# Check specific file coverage
pytest --cov=myapp.views.my_view --cov-report=term-missing
```

### Annotated Source

```bash
# Generate annotated HTML showing covered/uncovered lines
pytest --cov=. --cov-report=annotate
# Produces .cover files with + for covered, - for uncovered
```

## Advanced Coverage Options

### Context-Aware Coverage

```ini
# .coveragerc
[run]
parallel = True
concurrency = multiprocessing, thread

[report]
# Show which tests covered which lines
show_contexts = True
```

### Diff Coverage (Coverage for Changed Lines)

```bash
# Install diff-cover
pip install diff-cover

# Compare coverage against git branch
pytest --cov=. --cov-report=xml
diff-cover coverage.xml --compare-branch=origin/main --fail-under=80
```

### HTML Report with Branch Coverage

```bash
pytest --cov=. --cov-branch --cov-report=html
```

## Coverage Badges

### Generate Badge

```bash
# Install coverage-badge
pip install coverage-badge

# Generate badge from coverage data
coverage-badge -o coverage.svg -f
```

### In README

```markdown
![Coverage](coverage.svg)
```

## Best Practices

1. **Set minimum coverage threshold**: Use `--cov-fail-under` in CI
2. **Exclude test files**: Don't count test code in coverage
3. **Exclude migrations**: Django migrations are usually auto-generated
4. **Review uncovered lines**: HTML report helps identify missed code
5. **Use branch coverage**: More accurate than line coverage
6. **Combine with linting**: Coverage alone doesn't catch all issues
7. **Focus on critical paths**: 100% coverage isn't always necessary

## Common Issues

### Issue: Coverage not updating
```bash
# Clear coverage data
coverage erase

# Run fresh
pytest --cov=. --cov-report=html
```

### Issue: Source not found
```bash
# Explicitly set source
pytest --cov=myapp --cov-report=html
```

### Issue: Multiple Python versions
```bash
# Use .coveragerc with source path
[run]
source = myapp
```
