from pydantic import BaseModel


class TemplateCreate(BaseModel):

    day_of_week: int
    name: str


class TemplateResponse(TemplateCreate):

    id: int

    class Config:
        from_attributes = True