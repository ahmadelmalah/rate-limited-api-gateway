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
