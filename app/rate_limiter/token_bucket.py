import time
import logging
from typing import Tuple, Dict, Any, Optional
from redis.asyncio import Redis
from app.rate_limiter.base import RateLimiterInterface
from app.models import RateLimitConfig

logger = logging.getLogger(__name__)

class TokenBucketRateLimiter(RateLimiterInterface):
    # Lua script for atomic token bucket operations
    # Keys: [rate_limit_key]
    # Args: [capacity, refill_rate_per_sec, now_timestamp, requested_tokens, ttl]
    LUA_SCRIPT = """
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local rate = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    local requested = tonumber(ARGV[4])
    local ttl = tonumber(ARGV[5])

    local info = redis.call('HMGET', key, 'tokens', 'last_refill')
    local tokens = tonumber(info[1])
    local last_refill = tonumber(info[2])

    if not tokens then
        tokens = capacity
        last_refill = now
    end

    local delta = math.max(0, now - last_refill)
    local refill = delta * rate
    tokens = math.min(capacity, tokens + refill)

    local allowed = 0
    if tokens >= requested then
        tokens = tokens - requested
        allowed = 1
    end

    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
    redis.call('EXPIRE', key, ttl)

    return {allowed, tokens}
    """

    def __init__(self, redis: Redis):
        self.redis = redis
        self.script = self.redis.register_script(self.LUA_SCRIPT)

    async def is_allowed(self, key: str, config: RateLimitConfig) -> Tuple[bool, Dict[str, Any]]:
        """
        Checks if the request is allowed and consumes a token if it is.
        Note: This implementation combines check and consume for atomicity.
        """
        now = time.time()
        rate_per_sec = config.requests_per_minute / 60.0
        capacity = config.burst_size
        requested = 1
        # TTL: If no activity for a while, the bucket is full. 
        # We can expire the key after enough time has passed to fully refill.
        # Safety margin: 2 * capacity / rate
        # Ensure TTL is at least 1 second to prevent immediate expiration
        ttl = max(1, int((capacity / rate_per_sec) * 2)) if rate_per_sec > 0 else 3600

        redis_key = f"rate_limit:{key}"
        
        try:
            result = await self.script(
                keys=[redis_key],
                args=[capacity, rate_per_sec, now, requested, ttl]
            )
            
            allowed = bool(result[0])
            remaining = float(result[1])
            
            metadata = {
                "remaining": remaining,
                "limit": capacity,
                "reset_time": 0 # Token bucket doesn't have a hard reset time
            }
            
            return allowed, metadata
            
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            # Fail open (allow request) if Redis is down, or fail closed?
            # Usually fail open for resilience, but let's return False for safety in this demo.
            return False, {"error": str(e)}

    async def consume_token(self, key: str, config: RateLimitConfig) -> None:
        """
        Manually consumes a token. 
        In this implementation, is_allowed already consumes.
        This method is provided for interface compliance or manual adjustments.
        """
        # Re-uses the same script logic but ignores the result
        await self.is_allowed(key, config)
