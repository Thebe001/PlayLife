from sqlalchemy import Column, Integer, String, ForeignKey, Date
from app.db import Base


class Task(Base):

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    objective_id = Column(Integer, ForeignKey("objectives.id"), nullable=True)

    pillar_id = Column(Integer, ForeignKey("pillars.id"))

    title = Column(String, nullable=False)

    points = Column(Integer)

    difficulty = Column(String)

    status = Column(String, default="pending")

    due_date = Column(Date)