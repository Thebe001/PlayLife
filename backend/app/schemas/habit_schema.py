from pydantic import BaseModel
from datetime import date


class HabitBase(BaseModel):

    name: str
    pillar_id: int
    type: str
    points: int
    frequency: str


class HabitCreate(HabitBase):
    pass


class HabitResponse(HabitBase):

    id: int
    is_active: bool

    class Config:
        from_attributes = True


class HabitCheck(BaseModel):

    habit_id: int
    checked: bool