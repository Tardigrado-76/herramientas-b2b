import pytest
from httpx import ASGITransport, AsyncClient
from native_isolation_harness.dashboard.server import app

@pytest.mark.asyncio
async def test_native_isolation_dashboard_routes():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. UI route
        res = await client.get("/")
        assert res.status_code == 200
        assert "NATIVE ISOLATION HARNESS" in res.text

        # 2. SOC Incidents
        res = await client.get("/api/soc/incidents")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

        # 3. Sandbox execution (safe fibonacci)
        res = await client.post("/api/sandbox/execute", json={
            "script": "print('Test Sandbox execution')",
            "agent_id": "test-agent"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "Test Sandbox execution" in data["stdout"]
