from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.schemas.habit_schema import HabitCreate


# ── CRUD ──────────────────────────────────────────────────────────────────────

def create_habit(db: Session, data: HabitCreate) -> Habit:
    habit = Habit(**data.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def get_habits(db: Session) -> list[Habit]:
    return db.query(Habit).filter(Habit.is_active == True).all()


def get_habit_logs_today(db: Session) -> list[HabitLog]:
    today = date.today()
    return db.query(HabitLog).filter(HabitLog.date == today).all()


# ── Check / Uncheck ───────────────────────────────────────────────────────────

def check_habit(db: Session, habit_id: int) -> dict:
    """
    Coche une habitude pour aujourd'hui.
    - Bonne habitude  → points positifs
    - Mauvaise habitude → points négatifs
    - Idempotent : double appel retourne le log existant sans doublon
    """
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        return {"error": "Habitude introuvable"}

    today = date.today()

    existing = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == habit_id, HabitLog.date == today)
        .first()
    )
    if existing:
        return {"message": "Déjà cochée aujourd'hui", "log": existing}

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

    return {
        "message":      "Habitude cochée ✓",
        "points_earned": points,
        "log_id":        log.id,
    }


def uncheck_habit(db: Session, habit_id: int) -> dict:
    """Décoche une habitude pour aujourd'hui (supprime le log)."""
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


# ── Streak individuel ─────────────────────────────────────────────────────────

def get_habit_streak(db: Session, habit_id: int) -> dict:
    logs = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == habit_id, HabitLog.checked == True)
        .order_by(HabitLog.date.desc())
        .all()
    )

    if not logs:
        return {
            "current_streak": 0,
            "best_streak":    0,
            "last_checked":   None,
            "total_checks":   0,
        }

    checked_dates = {log.date for log in logs}
    total_checks  = len(checked_dates)
    last_checked  = max(checked_dates)

    # ── Streak actuel ──────────────────────────────────────────────────────
    # La fenêtre d'entrée : aujourd'hui OU hier (on laisse 24h de grâce)
    current_streak = 0
    start_date     = date.today()

    # Si la dernière coche est avant-hier ou plus → streak rompu
    if last_checked < start_date - timedelta(days=1):
        current_streak = 0
    else:
        # On commence à compter depuis la date la plus récente cochée
        check_date = last_checked
        while check_date in checked_dates:
            current_streak += 1
            check_date -= timedelta(days=1)

    # ── Record historique ──────────────────────────────────────────────────
    sorted_dates = sorted(checked_dates)
    best_streak  = 1
    run          = 1

    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] - sorted_dates[i - 1] == timedelta(days=1):
            run += 1
            best_streak = max(best_streak, run)
        else:
            run = 1

    return {
        "current_streak": current_streak,
        "best_streak":    best_streak,
        "last_checked":   last_checked.isoformat(),
        "total_checks":   total_checks,
    }


def get_all_habits_streaks(db: Session) -> list[dict]:
    """
    Retourne le streak de toutes les habitudes actives en un seul appel DB.
    Optimisé : charge tous les logs en une seule requête puis regroupe en Python.
    """
    habits = get_habits(db)
    if not habits:
        return []

    habit_ids = [h.id for h in habits]

    # Une seule requête pour tous les logs
    all_logs = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id.in_(habit_ids), HabitLog.checked == True)
        .all()
    )

    # Regrouper par habit_id
    from collections import defaultdict
    logs_by_habit: dict[int, list[date]] = defaultdict(list)
    for log in all_logs:
        logs_by_habit[log.habit_id].append(log.date)

    results = []
    for habit in habits:
        dates = sorted(logs_by_habit[habit.id])

        if not dates:
            results.append({
                "habit_id":       habit.id,
                "habit_name":     habit.name,
                "habit_type":     habit.type,
                "pillar_id":      habit.pillar_id,
                "current_streak": 0,
                "best_streak":    0,
                "last_checked":   None,
                "total_checks":   0,
            })
            continue

        checked_dates = set(dates)
        last_checked  = max(dates)
        total_checks  = len(dates)

        # Streak actuel
        # Streak actuel
        current_streak = 0
        if last_checked >= date.today() - timedelta(days=1):
            check_date = last_checked
            while check_date in checked_dates:
                current_streak += 1
                check_date -= timedelta(days=1)

        # Record
        best_streak = 1
        run         = 1
        for i in range(1, len(dates)):
            if dates[i] - dates[i - 1] == timedelta(days=1):
                run += 1
                best_streak = max(best_streak, run)
            else:
                run = 1

        results.append({
            "habit_id":       habit.id,
            "habit_name":     habit.name,
            "habit_type":     habit.type,
            "pillar_id":      habit.pillar_id,
            "current_streak": current_streak,
            "best_streak":    best_streak,
            "last_checked":   last_checked.isoformat(),
            "total_checks":   total_checks,
        })

    return results