"""
focus_routes.py
===============
Endpoints REST pour les sessions de focus.

Routes :
  POST /focus/log          — logue une session terminée (appelé par le Pomodoro frontend)
  GET  /focus/today        — stats du jour
  GET  /focus/by-pillar    — minutes par pilier (pour skill tree)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from app.db import get_db
from app.services.focus_service import (
    log_focus_session,
    get_focus_stats_today,
    get_focus_stats_by_pillar,
)

router = APIRouter(prefix="/focus", tags=["Focus"])


class FocusLogRequest(BaseModel):
    duration_min: int           = Field(..., ge=1, le=480,
                                        description="Durée réelle en minutes (1–480)")
    pillar_id:    Optional[int] = Field(None, description="Pilier concerné (optionnel)")
    habit_id:     Optional[int] = Field(None, description="Habitude liée (optionnel)")
    mode:         str           = Field("pomodoro", pattern="^(pomodoro|free)$")
    completed:    bool          = Field(True, description="False si session interrompue")


@router.post("/log")
def log_session(data: FocusLogRequest, db: Session = Depends(get_db)):
    """
    Appelé par le frontend Pomodoro quand une session se termine.
    Logue la session et génère les XP si complète.
    """
    return log_focus_session(
        db,
        duration_min=data.duration_min,
        pillar_id=data.pillar_id,
        habit_id=data.habit_id,
        mode=data.mode,
        completed=data.completed,
    )


@router.get("/today")
def focus_today(db: Session = Depends(get_db)):
    """Stats de focus pour aujourd'hui."""
    return get_focus_stats_today(db)


@router.get("/by-pillar")
def focus_by_pillar(db: Session = Depends(get_db)):
    """Minutes de focus complétées par pilier — utilisé par le skill tree."""
    return get_focus_stats_by_pillar(db)