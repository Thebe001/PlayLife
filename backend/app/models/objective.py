from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from app.db import Base


class Objective(Base):

    __tablename__ = "objectives"

    id = Column(Integer, primary_key=True, index=True)

    pillar_id = Column(Integer, ForeignKey("pillars.id"))

    title = Column(String, nullable=False)

    description = Column(String)

    horizon = Column(String)  # weekly / monthly / yearly

    deadline = Column(Date)

    completion_pct = Column(Float, default=0)

    status = Column(String, default="active")