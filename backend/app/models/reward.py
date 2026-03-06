from sqlalchemy import Column, Integer, String, Boolean
from app.db import Base


class Reward(Base):

    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    level_required = Column(String, default="bronze")  # bronze/silver/gold/diamond
    reward_type = Column(String, default="consumable")  # consumable / oneshot
    cooldown_days = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)