from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.challenge_service import generate_weekly_challenge

router = APIRouter(prefix="/challenges", tags=["Challenges"])


@router.get("/weekly")
def get_weekly_challenge(db: Session = Depends(get_db)):
    """
    Retourne le défi de la semaine généré automatiquement.
    Le défi change chaque lundi selon les données de la semaine précédente.
    """
    return generate_weekly_challenge(db)