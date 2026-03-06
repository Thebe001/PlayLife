"""
sanction_routes.py
==================
Endpoints REST pour les sanctions.

Routes :
  GET  /sanctions/             — liste toutes les sanctions configurées
  POST /sanctions/             — crée une sanction
  DELETE /sanctions/{id}       — supprime une sanction
  POST /sanctions/check        — déclenche la vérification manuelle (debug/cron)
  GET  /sanctions/logs         — historique des déclenchements
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db import get_db
from app.services.sanction_service import (
    check_and_trigger_sanctions,
    get_sanction_logs,
    create_sanction,
    get_sanctions,
    delete_sanction,
)

router = APIRouter(prefix="/sanctions", tags=["Sanctions"])


# ── Schémas ───────────────────────────────────────────────────────────────────

class SanctionCreate(BaseModel):
    name:              str   = Field(..., min_length=1, max_length=100)
    description:       str   = Field("", max_length=500)
    trigger_threshold: float = Field(..., ge=0.0, le=100.0,
                                     description="Score% en dessous duquel déclencher")
    consecutive_days:  int   = Field(..., ge=1, le=30,
                                     description="Nb jours consécutifs requis")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/")
def list_sanctions(db: Session = Depends(get_db)):
    """Liste toutes les sanctions configurées."""
    return get_sanctions(db)


@router.post("/")
def create_new_sanction(data: SanctionCreate, db: Session = Depends(get_db)):
    """
    Crée une sanction.
    Exemple : { name: "Pas de jeux vidéo", trigger_threshold: 40, consecutive_days: 2 }
    """
    return create_sanction(
        db,
        name=data.name,
        description=data.description,
        trigger_threshold=data.trigger_threshold,
        consecutive_days=data.consecutive_days,
    )


@router.delete("/{sanction_id}")
def remove_sanction(sanction_id: int, db: Session = Depends(get_db)):
    """Supprime une sanction et tous ses logs associés."""
    success = delete_sanction(db, sanction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sanction introuvable")
    return {"message": "Sanction supprimée ✓"}


@router.post("/check")
def trigger_check(db: Session = Depends(get_db)):
    """
    Déclenche manuellement la vérification des sanctions.
    Normalement appelé automatiquement après chaque recalcul de score.
    Utile pour le debug ou un éventuel cron job.
    """
    triggered = check_and_trigger_sanctions(db)
    return {
        "checked":   True,
        "triggered": triggered,
        "count":     len(triggered),
    }


@router.get("/logs")
def sanction_logs(limit: int = 50, db: Session = Depends(get_db)):
    """
    Historique des sanctions déclenchées.
    Retourne les `limit` derniers logs avec détail de la sanction.
    """
    return get_sanction_logs(db, limit=limit)