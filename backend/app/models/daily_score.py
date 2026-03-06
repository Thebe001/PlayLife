from sqlalchemy import Column, Integer, Float, Date, ForeignKey, UniqueConstraint
from datetime import date
from app.db import Base


class DailyScore(Base):

    __tablename__ = "daily_scores"
    __table_args__ = (UniqueConstraint("date", "pillar_id", name="uq_dailyscore_date_pillar"),)

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=date.today, nullable=False)
    pillar_id = Column(Integer, ForeignKey("pillars.id"), nullable=False)
    score_pct = Column(Float, default=0.0)
    points_earned = Column(Float, default=0.0)
    points_max = Column(Float, default=100.0)