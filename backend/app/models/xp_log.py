from sqlalchemy import Column, Integer, String, Date
from datetime import date
from app.db import Base


class XPLog(Base):

    __tablename__ = "xp_log"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(Date, default=date.today)

    xp_delta = Column(Integer)

    source = Column(String)

    description = Column(String)