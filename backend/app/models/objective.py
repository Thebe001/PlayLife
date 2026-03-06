from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Index
from app.db import Base


class Objective(Base):

    __tablename__ = "objectives"
    __table_args__ = (
        Index("ix_objectives_status",  "status"),
        Index("ix_objectives_horizon", "horizon"),
        Index("ix_objectives_pillar",  "pillar_id"),
    )

    id             = Column(Integer, primary_key=True, index=True)
    pillar_id      = Column(Integer, ForeignKey("pillars.id"), nullable=False)
    title          = Column(String, nullable=False)
    description    = Column(String)
    horizon        = Column(String)   # weekly / monthly / yearly
    deadline       = Column(Date)
    completion_pct = Column(Float, default=0)
    status         = Column(String, default="active")