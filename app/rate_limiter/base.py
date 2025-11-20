from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any

class RateLimiterInterface(ABC):
    """Abstract interface for rate limiting."""
    
    @abstractmethod
    async def is_allowed(self, key: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed.
        Returns: (allowed: bool, metadata: dict)
        Metadata should include: remaining, reset_time, retry_after
        """
        pass

    @abstractmethod
    async def consume_token(self, key: str) -> None:
        """Consume a token from the bucket."""
        pass
