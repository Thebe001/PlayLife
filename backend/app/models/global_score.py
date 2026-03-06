from sqlalchemy import Column, Integer, Float, Date
from datetime import date
from app.db import Base


class GlobalScore(Base):

    __tablename__ = "global_scores"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=date.today, nullable=False, unique=True)
    score_global = Column(Float, default=0.0)
    xp_earned = Column(Integer, default=0)