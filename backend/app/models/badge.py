from sqlalchemy import Column, Integer, String, Boolean
from app.db import Base


class Badge(Base):

    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    icon = Column(String)
    description = Column(String)
    condition_json = Column(String)
    is_custom = Column(Boolean, default=False)