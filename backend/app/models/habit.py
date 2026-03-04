from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.db import Base


class Habit(Base):

    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)

    pillar_id = Column(Integer, ForeignKey("pillars.id"))

    name = Column(String, nullable=False)

    type = Column(String)  # good or bad

    points = Column(Integer)

    frequency = Column(String)  # daily / weekly

    is_active = Column(Boolean, default=True)