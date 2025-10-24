# Tests for Stella Agent

This directory contains all the tests for the Stella Agent project.

## Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest fixtures and configuration
├── test_settings.py            # Unit tests for settings
└── test_api_integration.py     # Integration tests for API
```

## Running Tests

### All tests
```bash
pytest
```

### With coverage
```bash
pytest --cov=stella --cov-report=html
```

### Specific test file
```bash
pytest tests/test_settings.py
```

## Writing Tests

Follow pytest conventions and use the provided fixtures in conftest.py.
