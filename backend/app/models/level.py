from sqlalchemy import Column, Integer, String
from app.db import Base


class Level(Base):

    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    min_xp = Column(Integer)

    max_xp = Column(Integer)