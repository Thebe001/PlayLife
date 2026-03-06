from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from pydantic import BaseModel
from typing import Optional

from app.db import get_db
from app.models.review import Review
from app.models.global_score import GlobalScore
from app.models.habit_log import HabitLog
from app.models.habit import Habit
from app.models.journal_entry import JournalEntry
from app.models.objective import Objective

router = APIRouter(prefix="/reviews", tags=["Reviews"])


class ReviewCreate(BaseModel):
    type: str
    period_start: date
    period_end: date
    content: str
    edited_content: Optional[str] = None


def build_weekly_stats(db: Session, start: date, end: date) -> dict:
    scores = (
        db.query(GlobalScore)
        .filter(GlobalScore.date >= start, GlobalScore.date <= end)
        .all()
    )
    avg_score = round(sum(s.score_global for s in scores) / len(scores), 1) if scores else 0
    best_score = max((s.score_global for s in scores), default=0)
    days_logged = len(scores)

    logs = (
        db.query(HabitLog)
        .filter(HabitLog.date >= start, HabitLog.date <= end, HabitLog.checked == True)
        .all()
    )
    habits_checked = len(logs)

    entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.date >= start, JournalEntry.date <= end)
        .all()
    )
    avg_mood = round(sum(e.mood for e in entries) / len(entries), 1) if entries else 0

    objectives = (
        db.query(Objective)
        .filter(Objective.status == "completed")
        .all()
    )

    return {
        "avg_score": avg_score,
        "best_score": best_score,
        "days_logged": days_logged,
        "habits_checked": habits_checked,
        "avg_mood": avg_mood,
        "objectives_completed": len(objectives),
    }


@router.get("/")
def list_reviews(db: Session = Depends(get_db)):
    return db.query(Review).order_by(Review.period_start.desc()).all()


@router.post("/generate/weekly")
def generate_weekly_review(db: Session = Depends(get_db)):
    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    stats = build_weekly_stats(db, start, end)

    content = f"""📊 Review Hebdomadaire — {start.strftime('%d %b')} au {end.strftime('%d %b %Y')}

Score moyen : {stats['avg_score']}%
Meilleur score : {stats['best_score']}%
Jours loggés : {stats['days_logged']}/7
Habitudes cochées : {stats['habits_checked']}
Humeur moyenne : {stats['avg_mood']}/5
Objectifs complétés : {stats['objectives_completed']}

Points forts de la semaine :
→ [À compléter]

Points d'amélioration :
→ [À compléter]

Intentions pour la semaine prochaine :
→ [À compléter]
"""

    review = Review(
        type="weekly",
        period_start=start,
        period_end=end,
        content=content,
        llm_generated=False,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.post("/generate/monthly")
def generate_monthly_review(db: Session = Depends(get_db)):
    today = date.today()
    start = today.replace(day=1)
    if today.month == 12:
        end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    stats = build_weekly_stats(db, start, end)

    content = f"""📅 Review Mensuelle — {start.strftime('%B %Y')}

Score moyen du mois : {stats['avg_score']}%
Meilleur score : {stats['best_score']}%
Jours loggés : {stats['days_logged']}
Habitudes cochées : {stats['habits_checked']}
Humeur moyenne : {stats['avg_mood']}/5
Objectifs complétés : {stats['objectives_completed']}

Bilan du mois :
→ [À compléter]

Ce qui a bien fonctionné :
→ [À compléter]

Ce qui n'a pas fonctionné :
→ [À compléter]

Objectifs pour le mois prochain :
→ [À compléter]
"""

    review = Review(
        type="monthly",
        period_start=start,
        period_end=end,
        content=content,
        llm_generated=False,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.put("/{review_id}")
def update_review(review_id: int, data: ReviewCreate, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return {"error": "Introuvable"}
    review.edited_content = data.edited_content or data.content
    db.commit()
    db.refresh(review)
    return review


@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return {"error": "Introuvable"}
    db.delete(review)
    db.commit()
    return {"message": "Supprimée"}