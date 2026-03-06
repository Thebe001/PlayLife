from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime
from datetime import datetime, timezone
from app.db import Base


def _utcnow():
    return datetime.now(timezone.utc)


class Review(Base):

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    content = Column(String, nullable=False)
    llm_generated = Column(Boolean, default=False)
    edited_content = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utcnow)