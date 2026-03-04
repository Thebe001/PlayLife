from sqlalchemy import Column, Integer, Float, Date
from datetime import date
from app.db import Base


class GlobalScore(Base):

    __tablename__ = "global_scores"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(Date, default=date.today)

    score_global = Column(Float)

    xp_earned = Column(Integer)