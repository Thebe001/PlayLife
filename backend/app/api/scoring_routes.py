from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.db import get_db
from app.services.scoring_service import (
    calculate_daily_scores,
    calculate_global_score,
    get_today_summary,
)

router = APIRouter(prefix="/score", tags=["Score"])


@router.post("/daily")
def compute_daily_scores(db: Session = Depends(get_db)):
    return calculate_daily_scores(db)


@router.post("/global")
def compute_global_score(db: Session = Depends(get_db)):
    return calculate_global_score(db)


@router.get("/today")
def today_summary(db: Session = Depends(get_db)):
    """Résumé complet du jour pour le dashboard."""
    return get_today_summary(db)