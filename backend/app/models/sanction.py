from sqlalchemy import Column, Integer, String, Float
from app.db import Base


class Sanction(Base):

    __tablename__ = "sanctions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    trigger_threshold = Column(Float, default=40.0)  # score% en dessous duquel déclencher
    consecutive_days = Column(Integer, default=1)   # nb jours consécutifs requis