from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime
from app.db import Base


class RewardLog(Base):

    __tablename__ = "reward_logs"

    id = Column(Integer, primary_key=True, index=True)
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=False)
    consumed_at = Column(DateTime, default=datetime.utcnow)