from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.db import get_db
from app.schemas.habit_schema import HabitCreate, HabitResponse
from app.services.habit_service import (
    create_habit,
    get_habits,
    check_habit,
    uncheck_habit,
    get_habit_logs_today,
)
from app.services.xp_service import add_xp
from app.services.scoring_service import calculate_daily_scores, calculate_global_score

router = APIRouter(prefix="/habits", tags=["Habits"])


@router.post("/", response_model=HabitResponse)
def create_new_habit(habit: HabitCreate, db: Session = Depends(get_db)):
    return create_habit(db, habit)


@router.get("/", response_model=list[HabitResponse])
def read_habits(db: Session = Depends(get_db)):
    return get_habits(db)


@router.get("/today")
def habits_today(db: Session = Depends(get_db)):
    habits = get_habits(db)
    logs_today = get_habit_logs_today(db)
    checked_ids = {log.habit_id for log in logs_today}
    return [
        {
            "id": h.id,
            "name": h.name,
            "type": h.type,
            "points": h.points,
            "frequency": h.frequency,
            "pillar_id": h.pillar_id,
            "checked": h.id in checked_ids,
        }
        for h in habits
    ]


@router.post("/check/{habit_id}")
def check_habit_action(habit_id: int, db: Session = Depends(get_db)):
    result = check_habit(db, habit_id)

    # XP automatique si habitude cochée avec succès
    if "points_earned" in result:
        pts = result["points_earned"]
        if pts > 0:
            add_xp(db, pts, "habit")

    # Recalcul automatique des scores
    calculate_daily_scores(db)
    calculate_global_score(db)

    return result


@router.post("/uncheck/{habit_id}")
def uncheck_habit_action(habit_id: int, db: Session = Depends(get_db)):
    result = uncheck_habit(db, habit_id)

    # Recalcul automatique
    calculate_daily_scores(db)
    calculate_global_score(db)

    return result


@router.delete("/{habit_id}")
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    from app.models.habit import Habit
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        return {"error": "Introuvable"}
    habit.is_active = False
    db.commit()
    return {"message": "Habitude archivée"}