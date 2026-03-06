from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime, timezone
from app.db import Base


def _utcnow():
    return datetime.now(timezone.utc)


class SanctionLog(Base):

    __tablename__ = "sanction_logs"

    id = Column(Integer, primary_key=True, index=True)
    sanction_id = Column(Integer, ForeignKey("sanctions.id"), nullable=False)
    triggered_at = Column(DateTime, default=_utcnow)
    reason = Column(String)