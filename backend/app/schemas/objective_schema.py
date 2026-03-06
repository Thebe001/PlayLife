from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date


class ObjectiveCreate(BaseModel):
    pillar_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    horizon: Literal["weekly", "monthly", "yearly"] = "monthly"
    deadline: Optional[date] = None


class ObjectiveUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completion_pct: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[Literal["active", "completed", "abandoned"]] = None
    deadline: Optional[date] = None


class TaskCreate(BaseModel):
    objective_id: Optional[int] = None
    pillar_id: int
    title: str = Field(..., min_length=1, max_length=200)
    points: int = Field(20, ge=1, le=100)
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    due_date: Optional[date] = None
