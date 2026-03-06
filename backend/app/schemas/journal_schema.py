from pydantic import BaseModel, Field
from typing import Optional
from datetime import date as DateType


class JournalCreate(BaseModel):
    content: str = Field(..., min_length=1)
    mood:      Optional[int] = Field(None, ge=1, le=5)
    energy:    Optional[int] = Field(None, ge=1, le=5)
    tags:      Optional[str] = None
    highlight: Optional[str] = None


class JournalUpdate(BaseModel):
    content:   Optional[str] = Field(None, min_length=1)
    mood:      Optional[int] = Field(None, ge=1, le=5)
    energy:    Optional[int] = Field(None, ge=1, le=5)
    tags:      Optional[str] = None
    highlight: Optional[str] = None


class JournalResponse(JournalCreate):
    id: int
    date: DateType

    class Config:
        from_attributes = True