import pytest
from app.main import app
from app.models import TierType

@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "api-gateway"}

@pytest.mark.asyncio
async def test_proxy_flow_free_tier(client):
    # 1. Normal Request
    headers = {"X-API-Key": "user_free_1"}
    response = await client.get("/api/v1/resource", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "upstream"
    # Check that tier is correctly serialized (value of Enum)
    assert data["data"]["tier"] == TierType.FREE.value

    # 2. Rate Limit (Free tier = 5 RPM)
    # We already made 1 request. Make 4 more to hit limit.
    for _ in range(4):
        await client.get("/api/v1/resource", headers=headers)
    
    # Next one should fail
    response = await client.get("/api/v1/resource", headers=headers)
    assert response.status_code == 429
    assert "Too Many Requests" in response.json()["detail"]

@pytest.mark.asyncio
async def test_caching_flow(client):
    headers = {"X-API-Key": "premium_user"} # Premium has higher limits
    
    # 1. First Request (Miss)
    response = await client.get("/api/v1/cached-resource", headers=headers)
    assert response.status_code == 200
    assert response.json()["source"] == "upstream"
    
    # 2. Second Request (Hit)
    response = await client.get("/api/v1/cached-resource", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "cache"
    assert data["data"]["path"] == "api/v1/cached-resource"
