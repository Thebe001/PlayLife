from pydantic import BaseModel
from datetime import datetime


class PillarBase(BaseModel):

    name: str
    icon: str | None = None
    color: str | None = None
    weight_pct: float


class PillarCreate(PillarBase):
    pass


class PillarResponse(PillarBase):

    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True