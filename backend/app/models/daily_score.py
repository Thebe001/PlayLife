from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from datetime import date
from app.db import Base


class DailyScore(Base):

    __tablename__ = "daily_scores"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(Date, default=date.today)

    pillar_id = Column(Integer, ForeignKey("pillars.id"))

    score_pct = Column(Float)

    points_earned = Column(Integer)

    points_max = Column(Integer)