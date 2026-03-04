from pydantic import BaseModel
from datetime import date


class ReviewCreate(BaseModel):

    type: str
    period_start: date
    period_end: date
    content: str


class ReviewResponse(ReviewCreate):

    id: int

    class Config:
        from_attributes = True