"""
Pytest configuration and shared fixtures for Stella Agent tests.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient


@pytest.fixture
def test_client() -> Generator:
    """
    Provide a test client for the FastAPI application.
    
    Yields:
        TestClient instance
    """
    from main import app
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_session_id() -> str:
    """
    Provide a mock session ID for testing.
    
    Returns:
        Mock session ID string
    """
    return "test-session-123"


@pytest.fixture
def mock_correlation_id() -> str:
    """
    Provide a mock correlation ID for testing.
    
    Returns:
        Mock correlation ID string
    """
    return "test-correlation-456"


@pytest.fixture
def sample_speech_text() -> str:
    """
    Provide sample speech text for testing.
    
    Returns:
        Sample speech text
    """
    return "Preciso de 5 seringas de 10ml"


@pytest.fixture
def mock_settings():
    """
    Provide mock settings for testing.
    
    Returns:
        Dictionary with mock settings
    """
    return {
        'authentication': {
            'pin_length': 6,
            'max_pin_attempts': 3,
            'lockout_duration_minutes': 30,
        },
        'system': {
            'unit_id': 'TEST_UNIT_001',
            'log_level': 'DEBUG',
        },
        'validation': {
            'max_face_id_attempts': 3,
            'face_id_confidence_threshold': 0.8,
        }
    }


# Markers for test categorization
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "requires_env: mark test as requiring environment variables")
