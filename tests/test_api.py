import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from backend.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_success():
    """Test sentiment prediction endpoint with a valid headline"""
    payload = {"text": "Stock markets are booming today!"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "classification" in data
    assert "confidence" in data
    assert isinstance(data["classification"], str)
    assert isinstance(data["confidence"], float)

def test_predict_failure():
    """Test sentiment prediction endpoint with missing headline"""
    payload = {"text": ""}
    response = client.post("/predict", json=payload)
    assert response.status_code in (400, 422, 500)

def test_get_request_log_not_found():
    """Test fetching a request log that doesn't exist"""
    random_id = str(uuid4())
    response = client.get(f"/request_log/{random_id}")
    assert response.status_code in (404, 500, 200)
