from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_healthy():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "smokestack-ops"


def test_ready_endpoint_returns_ready():
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_grills_endpoint_returns_grills():
    response = client.get("/grills")

    assert response.status_code == 200

    data = response.json()

    assert "grills" in data
    assert len(data["grills"]) > 0
    assert "current_temp" in data["grills"][0]


def test_metrics_endpoint_returns_prometheus_metrics():
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "smokestack_api_requests_total" in response.text