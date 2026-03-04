from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.xp_service import add_xp, get_total_xp, get_current_level
from app.services.badge_service import check_badges

router = APIRouter(prefix="/gamification", tags=["Gamification"])


@router.post("/xp/{amount}")
def add_xp_action(amount: int, db: Session = Depends(get_db)):

    return add_xp(db, amount, "manual")


@router.get("/xp")
def get_xp(db: Session = Depends(get_db)):

    return {"total_xp": get_total_xp(db)}


@router.get("/level")
def current_level(db: Session = Depends(get_db)):

    return get_current_level(db)


@router.post("/badges/check")
def check_badges_action(db: Session = Depends(get_db)):

    return check_badges(db)