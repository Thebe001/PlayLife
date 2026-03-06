from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime, timezone
from app.db import Base


def _utcnow():
    return datetime.now(timezone.utc)


class RewardLog(Base):

    __tablename__ = "reward_logs"

    id = Column(Integer, primary_key=True, index=True)
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=False)
    consumed_at = Column(DateTime, default=_utcnow)