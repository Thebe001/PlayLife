from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field

from app.db import get_db
from app.schemas.pillar_schema import PillarCreate, PillarResponse
from app.services.pillar_service import (
    create_pillar,
    get_pillars,
    get_pillar_by_id,
    update_pillar,
    archive_pillar,
    get_weight_summary,
)

router = APIRouter(prefix="/pillars", tags=["Pillars"])


class PillarUpdate(BaseModel):
    name:       Optional[str]   = Field(None, min_length=1, max_length=100)
    icon:       Optional[str]   = None
    color:      Optional[str]   = None
    weight_pct: Optional[float] = Field(None, ge=0, le=100)


@router.get("/weight-summary")
def weight_summary(db: Session = Depends(get_db)):
    """
    Retourne la somme des poids actifs et le budget restant.
    Utilisé par le frontend pour afficher le warning en temps réel.
    """
    return get_weight_summary(db)


@router.get("/", response_model=list[PillarResponse])
def read_pillars(db: Session = Depends(get_db)):
    return get_pillars(db)


@router.post("/", response_model=PillarResponse)
def create_new_pillar(pillar: PillarCreate, db: Session = Depends(get_db)):
    # validate_weight_budget est appelé dans create_pillar — HTTP 422 si dépassement
    return create_pillar(db, pillar)


@router.put("/{pillar_id}", response_model=PillarResponse)
def update_existing_pillar(
    pillar_id: int,
    data: PillarUpdate,
    db: Session = Depends(get_db),
):
    updated = update_pillar(db, pillar_id, data.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Pilier introuvable")
    return updated


@router.delete("/{pillar_id}")
def delete_pillar(pillar_id: int, db: Session = Depends(get_db)):
    """Soft delete — archive le pilier sans perdre l'historique."""
    success = archive_pillar(db, pillar_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pilier introuvable")
    return {"message": "Pilier archivé ✓"}