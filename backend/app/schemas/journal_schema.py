from pydantic import BaseModel


class JournalCreate(BaseModel):

    content: str
    mood: int
    energy: int
    tags: str
    highlight: str


class JournalResponse(JournalCreate):

    id: int

    class Config:
        from_attributes = True