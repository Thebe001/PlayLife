from sqlalchemy import Column, Integer, String
from app.db import Base


class Level(Base):

    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    min_xp = Column(Integer, nullable=False)
    max_xp = Column(Integer, nullable=False)