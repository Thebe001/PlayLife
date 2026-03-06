from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey, UniqueConstraint
from datetime import date
from app.db import Base


class HabitLog(Base):

    __tablename__ = "habit_logs"
    __table_args__ = (UniqueConstraint("habit_id", "date", name="uq_habitlog_habit_date"),)

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    checked = Column(Boolean, default=False)
    points_earned = Column(Integer, default=0)