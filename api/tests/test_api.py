import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis for all tests — no real Redis connection needed."""
    with patch("main.redis_client") as mock_r:
        mock_r.ping.return_value = True
        mock_r.lpush.return_value = 1
        mock_r.get.return_value = b'{"status": "pending", "job_id": "test-123"}'
        mock_r.set.return_value = True
        yield mock_r


def test_root_returns_200():
    """GET / returns HTTP 200 with a JSON message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert "message" in response.json()


def test_health_returns_healthy():
    """GET /health returns {message: healthy}."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "healthy"}


def test_create_job_returns_job_id():
    """POST /jobs creates a job and returns a job_id."""
    response = client.post("/jobs", json={"task": "test-task"})
    assert response.status_code in (200, 201)
    data = response.json()
    assert "job_id" in data
    assert isinstance(data["job_id"], str)


def test_get_job_status_returns_status():
    """GET /jobs/{id} returns a status field."""
    response = client.get("/jobs/test-123")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_missing_job_returns_404():
    """GET /jobs/{nonexistent} returns 404 when job not found."""
    with patch("main.redis_client") as mock_r:
        mock_r.get.return_value = None
        response = client.get("/jobs/does-not-exist")
        assert response.status_code == 404


def test_create_job_pushes_to_redis(mock_redis):
    """POST /jobs calls redis lpush to enqueue the job."""
    client.post("/jobs", json={"task": "queue-test"})
    assert mock_redis.lpush.called or mock_redis.set.called


def test_health_calls_redis_ping(mock_redis):
    """GET /health calls redis ping to verify connectivity."""
    client.get("/health")
    assert mock_redis.ping.called
