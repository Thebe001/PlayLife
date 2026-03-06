from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, timedelta
from pydantic import BaseModel

from app.db import get_db
from app.models.review import Review
from app.models.global_score import GlobalScore
from app.models.daily_score import DailyScore
from app.models.habit_log import HabitLog
from app.models.journal_entry import JournalEntry
from app.models.pillar import Pillar
from app.services.review_service import generate_review_content, get_reviews, delete_review

router = APIRouter(prefix="/reviews", tags=["Reviews"])


class ReviewUpdate(BaseModel):
    type: str
    period_start: str
    period_end: str
    content: str
    edited_content: Optional[str] = None


# ── Génération ─────────────────────────────────────────

@router.post("/generate/{review_type}")
async def generate_review(review_type: str, db: Session = Depends(get_db)):
    """Génère une review hebdo ou mensuelle via LLM avec les vraies stats."""
    if review_type not in ("weekly", "monthly"):
        raise HTTPException(status_code=400, detail="Type invalide. Utilise 'weekly' ou 'monthly'.")

    today = date.today()

    if review_type == "weekly":
        # Lundi → aujourd'hui
        period_start = today - timedelta(days=today.weekday())
        period_end = today
    else:
        # 1er du mois → aujourd'hui
        period_start = today.replace(day=1)
        period_end = today

    # ── Collecte des stats ──────────────────────────────
    scores = (
        db.query(GlobalScore)
        .filter(GlobalScore.date >= period_start, GlobalScore.date <= period_end)
        .order_by(GlobalScore.date.asc())
        .all()
    )
    avg_score = round(sum(s.score_global for s in scores) / len(scores), 1) if scores else 0
    best_score = max((s.score_global for s in scores), default=0)
    worst_score = min((s.score_global for s in scores), default=0)

    total_checks = (
        db.query(HabitLog)
        .filter(
            HabitLog.date >= period_start,
            HabitLog.date <= period_end,
            HabitLog.checked == True,
        )
        .count()
    )

    pillars = db.query(Pillar).filter(Pillar.is_active == True).all()
    pillar_avgs = []
    for p in pillars:
        pillar_scores = (
            db.query(DailyScore)
            .filter(
                DailyScore.pillar_id == p.id,
                DailyScore.date >= period_start,
                DailyScore.date <= period_end,
            )
            .all()
        )
        if pillar_scores:
            avg = round(sum(ps.score_pct for ps in pillar_scores) / len(pillar_scores), 1)
            pillar_avgs.append({"name": p.name, "avg": avg})

    journal_entries = (
        db.query(JournalEntry)
        .filter(
            JournalEntry.date >= period_start,
            JournalEntry.date <= period_end,
        )
        .all()
    )
    mood_entries = [e for e in journal_entries if e.mood and e.mood > 0]
    avg_mood = round(sum(e.mood for e in mood_entries) / len(mood_entries), 1) if mood_entries else None
    highlights = [e.highlight for e in journal_entries if e.highlight]

    stats = {
        "type": review_type,
        "period_start": str(period_start),
        "period_end": str(period_end),
        "avg_score": avg_score,
        "best_score": best_score,
        "worst_score": worst_score,
        "total_days": len(scores),
        "total_habit_checks": total_checks,
        "pillar_avgs": pillar_avgs,
        "avg_mood": avg_mood,
        "highlights": highlights[:5],
    }

    # ── Génération du contenu ───────────────────────────
    content = await generate_review_content(stats)

    # ── Sauvegarde ──────────────────────────────────────
    review = Review(
        type=review_type,
        period_start=period_start,
        period_end=period_end,
        content=content,
        llm_generated=True,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


# ── CRUD ───────────────────────────────────────────────

@router.get("/")
def list_reviews(db: Session = Depends(get_db)):
    return get_reviews(db)


@router.put("/{review_id}")
def update_review(review_id: int, data: ReviewUpdate, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review introuvable")
    review.edited_content = data.edited_content
    db.commit()
    db.refresh(review)
    return review


@router.delete("/{review_id}")
def remove_review(review_id: int, db: Session = Depends(get_db)):
    result = delete_review(db, review_id)
    if not result:
        raise HTTPException(status_code=404, detail="Review introuvable")
    return {"message": "Supprimée"}