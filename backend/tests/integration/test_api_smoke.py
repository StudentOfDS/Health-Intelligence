import pytest

pytest.importorskip("httpx")
from fastapi.testclient import TestClient

from app.main import app


def test_health_and_capabilities_routes():
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    cap = client.get("/api/v1/platform/capabilities")
    assert cap.status_code == 200
    body = cap.json()
    assert body["backend_role"]
    assert "jwt_authn" in body["security"]
