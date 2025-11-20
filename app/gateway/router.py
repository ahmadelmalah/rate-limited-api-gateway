from fastapi import APIRouter, Request, HTTPException, Depends, Header
from typing import Optional
import httpx

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "api-gateway"}

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(path: str, request: Request):
    """
    Catch-all route to proxy requests to downstream services.
    """
    # 1. Extract API Key
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")

    # 2. Resolve Tier/Config (Mocked for now)
    # In a real app, we'd look up the key in DB/Redis to get the user's tier.
    from app.models import RateLimitConfig, TierType
    # Mock: "premium" key gets Premium tier, others get Free
    if "premium" in api_key:
        config = RateLimitConfig(tier=TierType.PREMIUM, requests_per_minute=60, burst_size=10)
    else:
        config = RateLimitConfig(tier=TierType.FREE, requests_per_minute=5, burst_size=1)

    # 3. Check Rate Limit
    rate_limiter = request.app.state.rate_limiter
    allowed, metadata = await rate_limiter.is_allowed(api_key, config)
    
    if not allowed:
        raise HTTPException(
            status_code=429, 
            detail="Too Many Requests",
            headers={
                "X-RateLimit-Remaining": str(metadata.get("remaining", 0)),
                "X-RateLimit-Limit": str(metadata.get("limit", 0)),
                "Retry-After": str(metadata.get("retry_after", 0))
            }
        )

    # 4. Check Cache (GET only)
    cache = request.app.state.cache
    cache_key = f"cache:{path}:{api_key}" # Simple cache key strategy
    
    if request.method == "GET":
        cached_response = await cache.get(cache_key)
        if cached_response:
            return {
                "data": cached_response,
                "source": "cache",
                "path": path
            }

    # 5. Proxy Request
    # For demo, we just echo back. In real life: await httpx.AsyncClient().request(...)
    # Let's simulate a downstream call
    response_data = {
        "message": "Proxy request successful",
        "path": path,
        "method": request.method,
        "tier": config.tier
    }

    # 6. Cache Response (GET only)
    if request.method == "GET":
        await cache.set(cache_key, response_data, ttl=60)

    return {
        "data": response_data,
        "source": "upstream",
        "rate_limit_remaining": metadata.get("remaining")
    }
