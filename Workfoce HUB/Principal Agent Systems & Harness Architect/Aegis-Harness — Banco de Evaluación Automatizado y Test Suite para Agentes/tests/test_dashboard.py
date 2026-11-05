import pytest
from httpx import ASGITransport, AsyncClient
from aegis.dashboard import app

@pytest.mark.asyncio
async def test_aegis_dashboard_routes():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/")
        assert res.status_code == 200
        assert "AEGIS-HARNESS" in res.text

        res = await client.get("/api/ledger")
        assert res.status_code == 200

        res = await client.post("/api/verify-ledger")
        assert res.status_code == 200
        assert res.json()["valid"] is True
