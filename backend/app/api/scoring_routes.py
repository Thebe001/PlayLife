from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.scoring_service import calculate_daily_scores, calculate_global_score

router = APIRouter(prefix="/score", tags=["Score"])


@router.post("/daily")
def compute_daily_scores(db: Session = Depends(get_db)):

    return calculate_daily_scores(db)


@router.post("/global")
def compute_global_score(db: Session = Depends(get_db)):

    return calculate_global_score(db)