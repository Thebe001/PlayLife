from pydantic import BaseModel, Field
from typing import Literal
from datetime import date


class HabitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    pillar_id: int
    type: Literal["good", "bad"]
    points: int = Field(..., ge=1, le=100)
    frequency: Literal["daily", "weekly"]


class HabitCreate(HabitBase):
    pass


class HabitResponse(HabitBase):
    id: int
    pillar_id: int
    is_active: bool

    model_config = {"from_attributes": True}