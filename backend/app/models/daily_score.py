from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from datetime import date
from app.db import Base


class DailyScore(Base):

    __tablename__ = "daily_scores"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=date.today, nullable=False)
    pillar_id = Column(Integer, ForeignKey("pillars.id"), nullable=False)
    score_pct = Column(Float, default=0.0)
    points_earned = Column(Float, default=0.0)
    points_max = Column(Float, default=100.0)