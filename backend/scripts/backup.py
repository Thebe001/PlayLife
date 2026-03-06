"""
Script de backup automatique — à lancer via le Task Scheduler Windows ou manuellement.

Usage :
    Double-clique sur backup.bat
    OU depuis PowerShell : python scripts/backup.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Ajouter le dossier backend au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import SessionLocal
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

BACKUP_DIR = Path(__file__).parent.parent / "backups"
BACKUP_DIR.mkdir(exist_ok=True)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def model_to_dict(obj) -> dict:
    return {c.name: str(getattr(obj, c.name)) for c in obj.__table__.columns}


def rotate(directory: Path, pattern: str, max_keep: int):
    files = sorted(directory.glob(pattern), key=lambda f: f.stat().st_mtime)
    while len(files) >= max_keep:
        removed = files.pop(0)
        removed.unlink()
        print(f"  🗑  Supprimé ancien backup : {removed.name}")


def run():
    ts  = now_utc().strftime("%Y%m%d_%H%M%S")
    out = BACKUP_DIR / f"auto_{ts}.json"

    print(f"[{now_utc().isoformat()}] 💾 Backup LifeForge OS...")

    db = SessionLocal()
    try:
        data = {
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
    finally:
        db.close()

    rotate(BACKUP_DIR, "auto_*.json", settings.MAX_AUTO_BACKUPS)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    size_kb = round(out.stat().st_size / 1024, 1)

    print(f"  ✅ Sauvegardé : {out.name} ({size_kb} KB)")
    print(f"  📦 Backups conservés : {len(list(BACKUP_DIR.glob('auto_*.json')))}/{settings.MAX_AUTO_BACKUPS}")


if __name__ == "__main__":
    run()