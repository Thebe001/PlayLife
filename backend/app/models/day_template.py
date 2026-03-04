from sqlalchemy import Column, Integer, String
from app.db import Base


class DayTemplate(Base):

    __tablename__ = "day_templates"

    id = Column(Integer, primary_key=True, index=True)

    day_of_week = Column(Integer)

    name = Column(String)