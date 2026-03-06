from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime, timezone
from app.db import Base


def _utcnow():
    return datetime.now(timezone.utc)


class FocusSession(Base):
    """
    Enregistre chaque session Pomodoro / free focus.
    Liée optionnellement à un pilier et à une habitude.
    """
    __tablename__ = "focus_sessions"

    id           = Column(Integer, primary_key=True, index=True)
    pillar_id    = Column(Integer, ForeignKey("pillars.id"),  nullable=True)
    habit_id     = Column(Integer, ForeignKey("habits.id"),   nullable=True)
    started_at   = Column(DateTime, default=_utcnow, nullable=False)
    ended_at     = Column(DateTime, nullable=True)
    duration_min = Column(Integer,  nullable=False)          # durée réelle en minutes
    mode         = Column(String,   default="pomodoro")      # pomodoro | free
    completed    = Column(Integer,  default=0)               # 1 = session complète, 0 = interrompue