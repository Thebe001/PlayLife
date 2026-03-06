from pydantic import BaseModel, Field
from datetime import datetime


class PillarBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: str | None = None
    color: str | None = None
    weight_pct: float = Field(..., ge=0, le=100)


class PillarCreate(PillarBase):
    pass


class PillarResponse(PillarBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True