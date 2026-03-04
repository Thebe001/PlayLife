from sqlalchemy.orm import Session
from datetime import date

from app.models.habit import Habit
from app.models.habit_log import HabitLog


def create_habit(db: Session, habit_data):

    habit = Habit(**habit_data.dict())

    db.add(habit)
    db.commit()
    db.refresh(habit)

    return habit


def get_habits(db: Session):

    return db.query(Habit).all()


def check_habit(db: Session, habit_id: int):

    habit = db.query(Habit).filter(Habit.id == habit_id).first()

    if not habit:
        return None

    log = HabitLog(
        habit_id=habit_id,
        checked=True,
        points_earned=habit.points
    )

    db.add(log)
    db.commit()

    return log