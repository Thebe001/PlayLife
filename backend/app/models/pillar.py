from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from app.db import Base


class Pillar(Base):

    __tablename__ = "pillars"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    icon = Column(String)

    color = Column(String)

    weight_pct = Column(Float)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)