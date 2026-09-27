"""API integration and backwards-compatibility tests."""

from fastapi.testclient import TestClient


def test_system_root(client: TestClient):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "northstar-security-platform"
    assert data["status"] == "ready"


def test_health_check(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["api"] is True
    assert data["database"] is True


def test_asset_crud_flow(client: TestClient):
    # 1. Create Asset
    create_payload = {
        "name": "Integration Test Server",
        "target": "10.99.12.5",
        "description": "Asset for automated integration testing",
        "environment": "staging",
        "owner": "QA Automation",
        "criticality": "medium",
        "tags": "testing,ci",
    }
    resp = client.post("/api/assets", json=create_payload)
    assert resp.status_code == 201
    asset_data = resp.json()
    asset_id = asset_data["id"]
    assert asset_data["name"] == "Integration Test Server"
    assert asset_data["target"] == "10.99.12.5"

    # 2. Get Asset by ID
    resp_get = client.get(f"/api/assets/{asset_id}")
    assert resp_get.status_code == 200
    assert resp_get.json()["target"] == "10.99.12.5"

    # 3. Update Asset
    update_payload = {"name": "Updated Test Server", "criticality": "high"}
    resp_put = client.put(f"/api/assets/{asset_id}", json=update_payload)
    assert resp_put.status_code == 200
    assert resp_put.json()["name"] == "Updated Test Server"
    assert resp_put.json()["criticality"] == "high"

    # 4. List Assets
    resp_list = client.get("/api/assets?search=Updated")
    assert resp_list.status_code == 200
    assert len(resp_list.json()) >= 1

    # 5. Delete Asset
    resp_del = client.delete(f"/api/assets/{asset_id}")
    assert resp_del.status_code == 204


def test_dashboard_endpoint(client: TestClient):
    resp = client.get("/api/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_assets" in data
    assert "open_vulnerabilities" in data
    assert "severity_breakdown" in data
    assert "trends_30d" in data


def test_schedules_crud(client: TestClient):
    # First get or create an asset
    asset_resp = client.post(
        "/api/assets",
        json={
            "name": "Sched Target",
            "target": "10.88.1.1",
            "environment": "staging",
            "owner": "Ops",
            "criticality": "low",
            "tags": "",
        },
    )
    asset_id = asset_resp.json()["id"]

    # Create schedule
    sched_payload = {
        "asset_id": asset_id,
        "profile": "full",
        "cadence": "Every 24 hours",
        "interval_hours": 24,
        "enabled": True,
    }
    resp = client.post("/api/schedules", json=sched_payload)
    assert resp.status_code == 201
    sched_id = resp.json()["id"]

    # List schedules
    list_resp = client.get("/api/schedules")
    assert list_resp.status_code == 200
    assert any(s["id"] == sched_id for s in list_resp.json())

    # Delete schedule
    del_resp = client.delete(f"/api/schedules/{sched_id}")
    assert del_resp.status_code == 204


def test_legacy_endpoints_backward_compatibility(client: TestClient):
    # Test /assets legacy
    resp_assets = client.get("/assets")
    assert resp_assets.status_code == 200
    assert isinstance(resp_assets.json(), list)

    # Test /scans/history legacy
    resp_hist = client.get("/scans/history")
    assert resp_hist.status_code == 200
    assert isinstance(resp_hist.json(), list)

    # Test /schedules legacy
    resp_sched = client.get("/schedules")
    assert resp_sched.status_code == 200
    assert isinstance(resp_sched.json(), list)
