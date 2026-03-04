from sqlalchemy import Column, Integer, String, Date
from datetime import date
from app.db import Base


class JournalEntry(Base):

    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(Date, default=date.today)

    content = Column(String)

    mood = Column(Integer)

    energy = Column(Integer)

    tags = Column(String)

    highlight = Column(String)