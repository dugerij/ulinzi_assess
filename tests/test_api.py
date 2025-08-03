import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.service_dependency import PredictionServiceDependency

@pytest.mark.anyio
async def test_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/")  
    assert response.status_code == 200
    assert response.json() == {"status": "API running"}

@pytest.mark.anyio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health") 
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.anyio
async def test_predict(monkeypatch):
    async def mock_submit_request(self, headline):
        return {"classification": "positive", "confidence": 0.95}

    monkeypatch.setattr(PredictionServiceDependency, "submit_request", mock_submit_request)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/predict", json={"text": "Stock prices are rising"})  

    assert response.status_code == 200
    json_data = response.json()
    assert "classification" in json_data
    assert "confidence" in json_data
