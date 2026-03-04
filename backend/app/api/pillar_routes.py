from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.pillar_schema import PillarCreate, PillarResponse
from app.services.pillar_service import create_pillar, get_pillars

router = APIRouter(prefix="/pillars", tags=["Pillars"])


@router.post("/", response_model=PillarResponse)
def create_new_pillar(
    pillar: PillarCreate,
    db: Session = Depends(get_db)
):

    return create_pillar(db, pillar)


@router.get("/", response_model=list[PillarResponse])
def read_pillars(db: Session = Depends(get_db)):

    return get_pillars(db)