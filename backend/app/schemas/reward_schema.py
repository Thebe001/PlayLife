from pydantic import BaseModel, Field
from typing import Optional, Literal


class RewardCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    level_required: Literal["bronze", "silver", "gold", "diamond"] = "bronze"
    reward_type: Literal["consumable", "oneshot"] = "consumable"
    cooldown_days: int = Field(0, ge=0)


class SanctionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    trigger_threshold: float = Field(40.0, ge=0, le=100)
    consecutive_days: int = Field(1, ge=1)
