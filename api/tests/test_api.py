import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis for all tests — no real Redis needed."""
    with patch("main.redis_client") as mock_r:
        mock_r.ping.return_value = True
        mock_r.lpush.return_value = 1
        mock_r.get.return_value = b'{"status": "pending", "job_id": "test-123"}'
        mock_r.set.return_value = True
        yield mock_r


def test_root_returns_200_and_json():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert "message" in response.json()


def test_health_returns_healthy():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "healthy"}


def test_create_job_returns_job_id():
    response = client.post("/jobs", json={"task": "test-task"})
    assert response.status_code in (200, 201)
    data = response.json()
    assert "job_id" in data


def test_get_job_status_returns_status():
    response = client.get("/jobs/test-123")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_invalid_job_id_returns_404_or_json():
    with patch("main.redis_client") as mock_r:
        mock_r.get.return_value = None
        response = client.get("/jobs/nonexistent-job")
        assert response.status_code in (404, 200)
        assert response.headers["content-type"].startswith("application/json")
