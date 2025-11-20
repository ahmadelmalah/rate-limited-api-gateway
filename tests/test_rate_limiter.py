import pytest
import asyncio
from app.rate_limiter.token_bucket import TokenBucketRateLimiter
from app.models import RateLimitConfig, TierType

@pytest.mark.asyncio
async def test_rate_limiter_allow_request(redis_client):
    limiter = TokenBucketRateLimiter(redis_client)
    config = RateLimitConfig(
        tier=TierType.FREE,
        requests_per_minute=60,
        burst_size=10
    )
    
    # Should be allowed
    allowed, metadata = await limiter.is_allowed("user_1", config)
    assert allowed is True
    assert metadata["remaining"] == 9.0

@pytest.mark.asyncio
async def test_rate_limiter_block_request(redis_client):
    limiter = TokenBucketRateLimiter(redis_client)
    config = RateLimitConfig(
        tier=TierType.FREE,
        requests_per_minute=60,
        burst_size=1  # Only 1 token
    )
    
    # First request: Allowed
    allowed, _ = await limiter.is_allowed("user_2", config)
    assert allowed is True
    
    # Second request: Blocked (bucket empty)
    allowed, metadata = await limiter.is_allowed("user_2", config)
    assert allowed is False
    assert metadata["remaining"] == 0.0

@pytest.mark.asyncio
async def test_rate_limiter_refill(redis_client):
    limiter = TokenBucketRateLimiter(redis_client)
    # High refill rate: 600 RPM = 10 requests per second = 1 token per 0.1s
    config = RateLimitConfig(
        tier=TierType.BASIC,
        requests_per_minute=600, 
        burst_size=1
    )
    
    # Consume the only token
    await limiter.is_allowed("user_3", config)
    
    # Verify empty
    allowed, metadata = await limiter.is_allowed("user_3", config)
    assert allowed is False
    
    # Wait for refill (0.1s + buffer)
    await asyncio.sleep(0.15)
    
    # Should be allowed again
    allowed, metadata = await limiter.is_allowed("user_3", config)
    assert allowed is True
