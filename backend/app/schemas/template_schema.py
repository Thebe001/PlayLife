from pydantic import BaseModel, Field


class TemplateCreate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    name: str = Field(..., min_length=1, max_length=100)


class TemplateResponse(TemplateCreate):
    id: int

    class Config:
        from_attributes = True