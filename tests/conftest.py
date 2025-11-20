import pytest
import pytest_asyncio
from fakeredis import aioredis

@pytest_asyncio.fixture
async def redis_client():
    # Use fakeredis for testing to simulate Redis without a real server
    # version=7 to support modern commands, though evalsha is old.
    redis = aioredis.FakeRedis(version=7)
    yield redis
    await redis.aclose()

@pytest_asyncio.fixture
async def client(redis_client):
    """
    Fixture that creates an AsyncClient and handles the FastAPI lifespan.
    This ensures app.state.redis/rate_limiter/cache are initialized.
    """
    from app.main import app, lifespan
    from httpx import AsyncClient, ASGITransport
    from unittest.mock import patch

    # Patch Redis.from_url to return our fakeredis client
    # We do this BEFORE entering lifespan so the app uses it
    with patch("app.main.Redis.from_url", return_value=redis_client):
        async with lifespan(app):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                yield ac
