from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey
from datetime import date
from app.db import Base


class HabitLog(Base):

    __tablename__ = "habit_logs"

    id = Column(Integer, primary_key=True, index=True)

    habit_id = Column(Integer, ForeignKey("habits.id"))

    date = Column(Date, default=date.today)

    checked = Column(Boolean, default=False)

    points_earned = Column(Integer, default=0)