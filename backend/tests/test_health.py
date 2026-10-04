from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "broken"}
    
def test_db_health_ok():
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"database": "ok"}