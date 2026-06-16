from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_brand_defaults():
    response = client.get("/api/brand")
    assert response.status_code == 200
    assert "company" in response.json()