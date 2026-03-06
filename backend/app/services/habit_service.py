from sqlalchemy.orm import Session
from datetime import date

from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.schemas.habit_schema import HabitCreate


def create_habit(db: Session, data: HabitCreate):
    habit = Habit(**data.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def get_habits(db: Session):
    return db.query(Habit).filter(Habit.is_active == True).all()


def check_habit(db: Session, habit_id: int):
    """Coche une habitude pour aujourd'hui. Gère good/bad habits."""

    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        return {"error": "Habitude introuvable"}

    today = date.today()

    # Vérifier si déjà cochée aujourd'hui
    existing = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == habit_id, HabitLog.date == today)
        .first()
    )
    if existing:
        return {"message": "Déjà cochée aujourd'hui", "log": existing}

    # Bad habit = points négatifs
    points = habit.points if habit.type == "good" else -abs(habit.points)

    log = HabitLog(
        habit_id=habit_id,
        date=today,
        checked=True,
        points_earned=points,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return {"message": "Habitude cochée ✓", "points_earned": points, "log_id": log.id}


def uncheck_habit(db: Session, habit_id: int):
    """Décoche une habitude pour aujourd'hui."""

    today = date.today()
    log = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == habit_id, HabitLog.date == today)
        .first()
    )
    if log:
        db.delete(log)
        db.commit()
        return {"message": "Habitude décochée"}
    return {"message": "Aucun log trouvé pour aujourd'hui"}


def get_habit_logs_today(db: Session):
    today = date.today()
    return db.query(HabitLog).filter(HabitLog.date == today).all()