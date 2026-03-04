from sqlalchemy import Column, Integer, ForeignKey, Date
from datetime import date
from app.db import Base


class BadgeUnlock(Base):

    __tablename__ = "badge_unlocks"

    id = Column(Integer, primary_key=True, index=True)

    badge_id = Column(Integer, ForeignKey("badges.id"))

    unlocked_at = Column(Date, default=date.today)