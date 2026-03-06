from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.db import get_db
from app.models.pillar import Pillar
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.models.objective import Objective
from app.models.task import Task
from app.models.global_score import GlobalScore
from app.models.daily_score import DailyScore
from app.models.journal_entry import JournalEntry
from app.models.review import Review
from app.models.badge import Badge
from app.models.badge_unlock import BadgeUnlock
from app.models.xp_log import XPLog
from app.models.reward import Reward
from app.models.sanction import Sanction

router = APIRouter(prefix="/backup", tags=["Backup"])


def model_to_dict(obj):
    return {c.name: str(getattr(obj, c.name)) for c in obj.__table__.columns}


@router.get("/export")
def export_all(db: Session = Depends(get_db)):
    """Export complet de toutes les données en JSON."""

    data = {
        "exported_at": datetime.utcnow().isoformat(),
        "version": "0.3.0",
        "pillars":       [model_to_dict(x) for x in db.query(Pillar).all()],
        "habits":        [model_to_dict(x) for x in db.query(Habit).all()],
        "habit_logs":    [model_to_dict(x) for x in db.query(HabitLog).all()],
        "objectives":    [model_to_dict(x) for x in db.query(Objective).all()],
        "tasks":         [model_to_dict(x) for x in db.query(Task).all()],
        "daily_scores":  [model_to_dict(x) for x in db.query(DailyScore).all()],
        "global_scores": [model_to_dict(x) for x in db.query(GlobalScore).all()],
        "journal":       [model_to_dict(x) for x in db.query(JournalEntry).all()],
        "reviews":       [model_to_dict(x) for x in db.query(Review).all()],
        "badges":        [model_to_dict(x) for x in db.query(Badge).all()],
        "badge_unlocks": [model_to_dict(x) for x in db.query(BadgeUnlock).all()],
        "xp_logs":       [model_to_dict(x) for x in db.query(XPLog).all()],
        "rewards":       [model_to_dict(x) for x in db.query(Reward).all()],
        "sanctions":     [model_to_dict(x) for x in db.query(Sanction).all()],
    }

    return JSONResponse(
        content=data,
        headers={
            "Content-Disposition": f"attachment; filename=lifeforge_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        }
    )


@router.get("/stats")
def backup_stats(db: Session = Depends(get_db)):
    """Stats rapides sur le volume de données."""
    return {
        "pillars":      db.query(Pillar).count(),
        "habits":       db.query(Habit).count(),
        "habit_logs":   db.query(HabitLog).count(),
        "objectives":   db.query(Objective).count(),
        "journal":      db.query(JournalEntry).count(),
        "reviews":      db.query(Review).count(),
        "xp_logs":      db.query(XPLog).count(),
    }