import json
from typing import Optional, Any
from redis.asyncio import Redis
from app.cache.base import CacheInterface

class RedisCache(CacheInterface):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Optional[Any]:
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value.decode("utf-8") if isinstance(value, bytes) else value
        return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        # Serialize complex types to JSON
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.redis.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)
