from sqlalchemy import Column, Integer, String, Date
from app.db import Base


class Review(Base):

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    type = Column(String)  # weekly / monthly / yearly

    period_start = Column(Date)

    period_end = Column(Date)

    content = Column(String)

    llm_generated = Column(String)

    edited_content = Column(String)