"""
Integration tests for API routes.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestAPIRoutes:
    """Tests for API routes."""

    def test_root_endpoint(self, test_client):
        """Test the root endpoint returns status."""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Stella Agent API"
        assert data["status"] == "running"
        assert "version" in data
        assert "endpoints" in data

    def test_docs_endpoint(self, test_client):
        """Test that API documentation is accessible."""
        response = test_client.get("/docs")
        assert response.status_code == 200

    def test_redoc_endpoint(self, test_client):
        """Test that ReDoc documentation is accessible."""
        response = test_client.get("/redoc")
        assert response.status_code == 200


@pytest.mark.integration
class TestSpeechAPI:
    """Tests for Speech API endpoints."""

    def test_speech_process_empty_text(self, test_client, mock_session_id, mock_correlation_id):
        """Test that empty text is rejected."""
        response = test_client.post(
            "/speech/process",
            json={
                "session_id": mock_session_id,
                "correlation_id": mock_correlation_id,
                "data": {"text": ""}
            }
        )
        assert response.status_code == 400

    def test_speech_process_too_long(self, test_client, mock_session_id, mock_correlation_id):
        """Test that text over 250 characters is rejected."""
        long_text = "a" * 251
        response = test_client.post(
            "/speech/process",
            json={
                "session_id": mock_session_id,
                "correlation_id": mock_correlation_id,
                "data": {"text": long_text}
            }
        )
        assert response.status_code == 400
