import pytest


@pytest.mark.anyio
async def test_health_check(client):
    """应用启动后 /health 返回 200"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
