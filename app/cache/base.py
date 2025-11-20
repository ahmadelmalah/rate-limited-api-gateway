from abc import ABC, abstractmethod
from typing import Optional, Any

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
