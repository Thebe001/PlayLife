import os
import json
from pathlib import Path
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.config import settings
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
from app.models.reward_log import RewardLog
from app.models.sanction import Sanction
from app.models.sanction_log import SanctionLog
from app.models.level import Level
from app.models.day_template import DayTemplate
from app.models.template_item import TemplateItem

router = APIRouter(prefix="/backup", tags=["Backup"])

BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def model_to_dict(obj) -> dict:
    return {c.name: str(getattr(obj, c.name)) for c in obj.__table__.columns}


def collect_all_data(db: Session) -> dict:
    return {
        "exported_at":   now_utc().isoformat(),
        "version":       settings.APP_VERSION,
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
        "reward_logs":   [model_to_dict(x) for x in db.query(RewardLog).all()],
        "sanctions":     [model_to_dict(x) for x in db.query(Sanction).all()],
        "sanction_logs": [model_to_dict(x) for x in db.query(SanctionLog).all()],
        "levels":        [model_to_dict(x) for x in db.query(Level).all()],
        "day_templates": [model_to_dict(x) for x in db.query(DayTemplate).all()],
        "template_items":[model_to_dict(x) for x in db.query(TemplateItem).all()],
    }


def _rotate_backups():
    files = sorted(BACKUP_DIR.glob("auto_*.json"), key=os.path.getmtime)
    while len(files) >= settings.MAX_AUTO_BACKUPS:
        files.pop(0).unlink()


@router.get("/export")
def export_all(db: Session = Depends(get_db)):
    ts   = now_utc().strftime("%Y%m%d_%H%M%S")
    data = collect_all_data(db)
    _rotate_backups()
    local_path = BACKUP_DIR / f"auto_{ts}.json"
    local_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return JSONResponse(
        content=data,
        headers={"Content-Disposition": f"attachment; filename=lifeforge_backup_{ts}.json"},
    )


@router.post("/save-local")
def save_local(db: Session = Depends(get_db)):
    ts   = now_utc().strftime("%Y%m%d_%H%M%S")
    data = collect_all_data(db)
    _rotate_backups()
    local_path = BACKUP_DIR / f"auto_{ts}.json"
    local_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "message":  "Backup sauvegardé ✓",
        "filename": local_path.name,
        "size_kb":  round(local_path.stat().st_size / 1024, 1),
    }


@router.get("/list")
def list_backups():
    files = sorted(BACKUP_DIR.glob("auto_*.json"), key=os.path.getmtime, reverse=True)
    return [
        {
            "filename": f.name,
            "size_kb":  round(f.stat().st_size / 1024, 1),
            "date":     datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat(),
        }
        for f in files
    ]


@router.get("/stats")
def backup_stats(db: Session = Depends(get_db)):
    backups = sorted(BACKUP_DIR.glob("auto_*.json"), key=os.path.getmtime, reverse=True)
    last_backup = (
        datetime.fromtimestamp(backups[0].stat().st_mtime, tz=timezone.utc).isoformat()
        if backups else None
    )
    return {
        "data": {
            "pillars":    db.query(Pillar).count(),
            "habits":     db.query(Habit).count(),
            "habit_logs": db.query(HabitLog).count(),
            "objectives": db.query(Objective).count(),
            "journal":    db.query(JournalEntry).count(),
            "reviews":    db.query(Review).count(),
            "xp_logs":    db.query(XPLog).count(),
        },
        "backups": {
            "count":       len(backups),
            "last_backup": last_backup,
        },
    }