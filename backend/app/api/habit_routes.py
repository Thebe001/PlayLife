from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.habit_schema import HabitCreate, HabitResponse
from app.services.habit_service import (
    create_habit,
    get_habits,
    check_habit,
    uncheck_habit,
    get_habit_logs_today,
    get_habit_streak,
    get_all_habits_streaks,
)
from app.services.xp_service import add_xp
from app.services.scoring_service import calculate_daily_scores, calculate_global_score

router = APIRouter(prefix="/habits", tags=["Habits"])


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.post("/", response_model=HabitResponse)
def create_new_habit(habit: HabitCreate, db: Session = Depends(get_db)):
    return create_habit(db, habit)


@router.get("/", response_model=list[HabitResponse])
def read_habits(db: Session = Depends(get_db)):
    return get_habits(db)


@router.get("/today")
def habits_today(db: Session = Depends(get_db)):
    """
    Retourne les habitudes du jour avec leur état coché/décoché
    ET leur streak actuel — affichage enrichi dans le planning.
    """
    habits      = get_habits(db)
    logs_today  = get_habit_logs_today(db)
    checked_ids = {log.habit_id for log in logs_today}

    # Streaks en une seule requête groupée
    streaks_list = get_all_habits_streaks(db)
    streaks_map  = {s["habit_id"]: s for s in streaks_list}

    return [
        {
            "id":             h.id,
            "name":           h.name,
            "type":           h.type,
            "points":         h.points,
            "frequency":      h.frequency,
            "pillar_id":      h.pillar_id,
            "checked":        h.id in checked_ids,
            "current_streak": streaks_map.get(h.id, {}).get("current_streak", 0),
            "best_streak":    streaks_map.get(h.id, {}).get("best_streak", 0),
        }
        for h in habits
    ]


# ── Check / Uncheck ───────────────────────────────────────────────────────────

@router.post("/check/{habit_id}")
def check_habit_action(habit_id: int, db: Session = Depends(get_db)):
    """
    Coche une habitude :
    - Ajoute les XP si points > 0
    - Recalcule les scores daily + global
    - Retourne les points gagnés + streak mis à jour
    """
    result = check_habit(db, habit_id)

    if "points_earned" in result:
        pts = result["points_earned"]
        if pts > 0:
            add_xp(db, pts, "habit")

    calculate_daily_scores(db)
    calculate_global_score(db)

    # Streak mis à jour après la coche
    streak = get_habit_streak(db, habit_id)
    result["streak"] = streak

    return result


@router.post("/uncheck/{habit_id}")
def uncheck_habit_action(habit_id: int, db: Session = Depends(get_db)):
    """
    Décoche une habitude et recalcule les scores.
    """
    result = uncheck_habit(db, habit_id)

    calculate_daily_scores(db)
    calculate_global_score(db)

    streak = get_habit_streak(db, habit_id)
    result["streak"] = streak

    return result


# ── Streaks ───────────────────────────────────────────────────────────────────

@router.get("/streaks")
def all_streaks(db: Session = Depends(get_db)):
    """
    Retourne le streak actuel + record de toutes les habitudes actives.
    Optimisé : une seule requête DB groupée.
    """
    return get_all_habits_streaks(db)


@router.get("/streaks/{habit_id}")
def single_streak(habit_id: int, db: Session = Depends(get_db)):
    """
    Streak détaillé pour une habitude spécifique.
    Retourne : current_streak, best_streak, last_checked, total_checks.
    """
    habit = db.query(__import__("app.models.habit", fromlist=["Habit"]).Habit).filter_by(id=habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habitude introuvable")
    return get_habit_streak(db, habit_id)


# ── Suppression (soft delete) ─────────────────────────────────────────────────

@router.delete("/{habit_id}")
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    from app.models.habit import Habit
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habitude introuvable")
    habit.is_active = False
    db.commit()
    return {"message": "Habitude archivée ✓"}