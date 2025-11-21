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

from app.logging_config import setup_logging
import logging
import time
from fastapi import Request

# Setup logging immediately
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up API Gateway...")
    redis_client = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    app.state.redis = redis_client
    app.state.rate_limiter = TokenBucketRateLimiter(redis_client)
    app.state.cache = RedisCache(redis_client)
    
    yield
    
    # Shutdown
    logger.info("Shutting down API Gateway...")
    await redis_client.aclose()

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    log_data = {
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(process_time, 2),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
    }
    
    # Log at INFO level
    logger.info("Request processed", extra={"extra_info": log_data})
    
    return response

app.include_router(gateway_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Rate Limited API Gateway"}
