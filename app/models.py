from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

class TierType(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class RateLimitConfig(BaseModel):
    tier: TierType
    requests_per_minute: int = Field(..., gt=0, description="Max requests allowed per minute")
    burst_size: int = Field(..., gt=0, description="Max burst size allowed")

class APIKey(BaseModel):
    key: str
    tier: TierType
    user_id: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
