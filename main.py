import asyncio
import time
from enum import Enum
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

# -----------------------------------------------------------------------------
# INTERFACES
# -----------------------------------------------------------------------------

class CacheInterface(ABC):
    """Abstract interface for caching."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

    @abstractmethod
    async def get_stats(self) -> Dict[str, int]:
        """Return cache hit/miss statistics."""
        pass

# -----------------------------------------------------------------------------
# IMPLEMENTATION Section
# -----------------------------------------------------------------------------

class TokenBucketRateLimiter(RateLimiterInterface):
    def __init__(self, config_map: Dict[TierType, RateLimitConfig]):
        self.config_map = config_map
        # TODO: Initialize storage (Redis client or in-memory dict)
        # Store: {api_key: {"tokens": float, "last_refill": timestamp}}
        pass

    async def is_allowed(self, api_key: str) -> Tuple[bool, Dict[str, Any]]:
        # TODO: Implement token bucket logic
        # Steps:
        # 1. Get current token count for api_key
        # 2. Calculate tokens to add based on time elapsed
        # 3. Check if at least 1 token available
        # 4. Return result with metadata
        pass

    async def consume_token(self, api_key: str) -> None:
        # TODO: Consume one token from the bucket
        pass

class InMemoryCache(CacheInterface):
    """
    Thread-safe operations
    Automatic expiration
    Size limits
    Track hit/miss for metrics
    """
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        # TODO: Initialize cache storage
        # Consider: OrderedDict for LRU, store (value, expiry_time)
        # Track hits and misses
        pass

    async def get(self, key: str) -> Optional[Any]:
        # TODO: Implement with TTL check
        # Update hit/miss counters
        pass

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        # TODO: Implement with LRU eviction
        # Store expiry_time = current_time + ttl
        pass

    async def delete(self, key: str) -> None:
        # TODO: Remove key from cache
        pass

    async def get_stats(self) -> Dict[str, int]:
        # TODO: Return {"hits": X, "misses": Y, "size": Z}
        pass

class APIGateway:
    """
    Route requests to downstream services
    Apply rate limiting
    Handle caching for GET requests
    Implement retry logic with exponential backoff
    """
    def __init__(self, rate_limiter: RateLimiterInterface, cache: CacheInterface):
        self.rate_limiter = rate_limiter
        self.cache = cache

    async def handle_request(self, api_key: str, method: str, endpoint: str, 
                           body: Optional[Dict] = None, max_retries: int = 3):
        # TODO: Main request handler
        # Steps:
        # 1. Check rate limit
        # 2. For GET requests, check cache first
        # 3. Forward to downstream service with retry logic
        # 4. Cache successful GET responses
        # 5. Return response
        
        # Error handling:
        # Rate limit exceeded: return 429
        # Timeout: retry with exponential backoff
        # Server error: retry or fail gracefully
        pass

    async def forward_to_downstream(self, endpoint: str, method: str, 
                                  body: Optional[Dict] = None, timeout: int = 5):
        # TODO: Forward request to downstream service
        # Simulate or implement actual HTTP call
        # Handle timeouts and connection errors
        pass

    async def health_check(self) -> Dict[str, Any]:
        # TODO: Implement health check
        # Return status of rate limiter, cache, and overall system
        # Include cache statistics
        pass

# -----------------------------------------------------------------------------
# TESTS
# -----------------------------------------------------------------------------

class TestRateLimiter:
    # TODO: Write unit tests
    # Test cases:
    # - Token bucket allows requests within limit
    # - Requests blocked when tokens exhausted
    # - Tokens refill over time correctly
    # - Burst capacity works as expected
    # - Concurrent requests handled properly
    # - Different tiers have different limits
    pass

class TestCache:
    # TODO: Write cache tests
    # Test cases:
    # - Set and get work correctly
    # - TTL expiration works
    # - LRU eviction works when cache full
    # - Cache miss returns None
    # - Hit/miss statistics accurate
    pass

class TestAPIGateway:
    # TODO: Write gateway tests
    # Test cases:
    # - Rate limiting applied correctly
    # - Cache used for GET requests
    # - Retry logic works on failures
    # - Timeout handling
    # - Health check returns correct status
    pass

# -----------------------------------------------------------------------------
# EXAMPLE USAGE
# -----------------------------------------------------------------------------

async def main():
    # Setup configurations
    configs = {
        TierType.FREE: RateLimitConfig(TierType.FREE, 10, burst_size=15),
        TierType.BASIC: RateLimitConfig(TierType.BASIC, 100, burst_size=150),
        TierType.PREMIUM: RateLimitConfig(TierType.PREMIUM, 1000, burst_size=1500),
    }

    # Initialize components
    rate_limiter = TokenBucketRateLimiter(configs)
    cache = InMemoryCache(max_size=1000)
    gateway = APIGateway(rate_limiter, cache)

    # Simulate requests
    api_key = "test_key_123"
    
    print("Starting simulation...")

    # Example: Make a GET request
    # response = await gateway.handle_request(
    #     api_key=api_key,
    #     method="GET", 
    #     endpoint="/api/users/123"
    # )
    # print(f"Response: {response}")

    # Check cache stats
    cache_stats = await cache.get_stats()
    print(f"Cache Stats: {cache_stats}")

    # Check health
    health = await gateway.health_check()
    print(f"Health: {health}")

    # Simulate burst traffic
    print("\nSimulating burst traffic...")
    for i in range(20):
        allowed, metadata = await rate_limiter.is_allowed(api_key)
        print(f"Request {i+1}: Allowed={allowed}, Remaining={metadata.get('remaining', 0)}")
        
        if allowed:
            await rate_limiter.consume_token(api_key)
        
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())