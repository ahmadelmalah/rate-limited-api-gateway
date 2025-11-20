from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis.asyncio import Redis

from app.config import settings
from app.gateway.router import router as gateway_router
from app.rate_limiter.token_bucket import TokenBucketRateLimiter
from app.cache.redis_cache import RedisCache

# Global state
redis_client: Redis = None
rate_limiter: TokenBucketRateLimiter = None
cache: RedisCache = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    redis_client = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    app.state.redis = redis_client
    app.state.rate_limiter = TokenBucketRateLimiter(redis_client)
    app.state.cache = RedisCache(redis_client)
    
    yield
    
    # Shutdown
    await redis_client.aclose()

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

app.include_router(gateway_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Rate Limited API Gateway"}
