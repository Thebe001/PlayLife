from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.db import get_db
from app.models.global_score import GlobalScore
from app.models.daily_score import DailyScore
from app.models.pillar import Pillar
from app.models.habit_log import HabitLog
from app.models.journal_entry import JournalEntry
from app.models.xp_log import XPLog

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/heatmap")
def get_heatmap(db: Session = Depends(get_db)):
    """Retourne les scores des 365 derniers jours pour la heatmap."""
    today = date.today()
    start = today - timedelta(days=364)

    scores = (
        db.query(GlobalScore)
        .filter(GlobalScore.date >= start)
        .order_by(GlobalScore.date.asc())
        .all()
    )

    score_map = {str(s.date): s.score_global for s in scores}

    result = []
    for i in range(365):
        d = start + timedelta(days=i)
        ds = str(d)
        result.append({
            "date": ds,
            "score": score_map.get(ds, None),
        })

    return result


@router.get("/progression")
def get_progression(days: int = 30, db: Session = Depends(get_db)):
    """Retourne la progression globale + par pilier sur N jours."""
    today = date.today()
    start = today - timedelta(days=days - 1)

    global_scores = (
        db.query(GlobalScore)
        .filter(GlobalScore.date >= start)
        .order_by(GlobalScore.date.asc())
        .all()
    )

    pillars = db.query(Pillar).filter(Pillar.is_active == True).all()

    pillar_data = {}
    for pillar in pillars:
        daily = (
            db.query(DailyScore)
            .filter(DailyScore.pillar_id == pillar.id, DailyScore.date >= start)
            .order_by(DailyScore.date.asc())
            .all()
        )
        pillar_data[pillar.name] = {
            "color": pillar.color,
            "scores": [{"date": str(d.date), "score": d.score_pct} for d in daily],
        }

    return {
        "global": [{"date": str(s.date), "score": s.score_global} for s in global_scores],
        "pillars": pillar_data,
    }


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    """Stats clés : moyenne 7j, 30j, meilleur jour, total habitudes, XP réel."""
    today = date.today()

    def avg_score(days: int) -> float:
        start = today - timedelta(days=days - 1)
        scores = db.query(GlobalScore).filter(GlobalScore.date >= start).all()
        if not scores:
            return 0.0
        return round(sum(s.score_global for s in scores) / len(scores), 1)

    best = (
        db.query(GlobalScore)
        .order_by(GlobalScore.score_global.desc())
        .first()
    )

    total_checks = (
        db.query(HabitLog)
        .filter(HabitLog.checked == True)
        .count()
    )

    # ✅ Fix : XP total depuis XPLog (source réelle), pas GlobalScore
    xp_sum = db.query(func.sum(XPLog.xp_delta)).scalar() or 0

    # Mood moyen — ignorer les entrées sans mood (None ou 0)
    entries_with_mood = (
        db.query(JournalEntry)
        .filter(JournalEntry.mood != None, JournalEntry.mood > 0)
        .all()
    )
    avg_mood = (
        round(sum(e.mood for e in entries_with_mood) / len(entries_with_mood), 1)
        if entries_with_mood else 0
    )

    total_entries = db.query(JournalEntry).count()

    return {
        "avg_7d": avg_score(7),
        "avg_30d": avg_score(30),
        "best_score": best.score_global if best else 0,
        "best_score_date": str(best.date) if best else None,
        "total_habit_checks": total_checks,
        "total_xp": int(xp_sum),
        "avg_mood": avg_mood,
        "total_journal_entries": total_entries,
    }