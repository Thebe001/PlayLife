"""
focus_service.py
================
Logique métier pour les sessions de focus (Pomodoro / free).

Chaque session complète :
- Est persistée en DB (pilier, habitude liée, durée)
- Génère des XP (1 XP par minute de focus complétée)
- Met à jour les stats du skill tree du pilier concerné
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, date

from app.models.focus_session import FocusSession
from app.models.xp_log import XPLog


# ── XP par minute de focus ────────────────────────────────────────────────────
XP_PER_FOCUS_MINUTE = 1   # 25 min Pomodoro = 25 XP


def log_focus_session(
    db:           Session,
    duration_min: int,
    pillar_id:    int | None = None,
    habit_id:     int | None = None,
    mode:         str        = "pomodoro",
    completed:    bool       = True,
) -> dict:
    """
    Logue une session de focus terminée.

    - Crée un FocusSession en DB
    - Ajoute les XP si la session est complète
    - Retourne le résumé (xp_earned, session_id)
    """
    now = datetime.now(timezone.utc)

    # Durée minimale : 1 minute, sinon on ignore
    if duration_min < 1:
        return {"error": "Durée trop courte (< 1 min)"}

    session = FocusSession(
        pillar_id=pillar_id,
        habit_id=habit_id,
        started_at=now,
        ended_at=now,
        duration_min=duration_min,
        mode=mode,
        completed=1 if completed else 0,
    )
    db.add(session)

    xp_earned = 0
    if completed:
        xp_earned = duration_min * XP_PER_FOCUS_MINUTE
        xp_log = XPLog(
            xp_delta=xp_earned,
            source="focus",
            description=f"Focus session {mode} — {duration_min} min",
        )
        db.add(xp_log)

    db.commit()
    db.refresh(session)

    return {
        "session_id":  session.id,
        "duration_min": duration_min,
        "xp_earned":   xp_earned,
        "mode":        mode,
        "completed":   completed,
        "pillar_id":   pillar_id,
        "habit_id":    habit_id,
    }


def get_focus_stats_today(db: Session) -> dict:
    """
    Stats de focus pour aujourd'hui :
    - total_sessions : nombre de sessions
    - total_minutes  : minutes totales
    - completed_sessions : sessions complètes
    - xp_earned : XP générés par les sessions focus aujourd'hui
    """
    today = date.today()

    sessions = (
        db.query(FocusSession)
        .filter(func.date(FocusSession.started_at) == today)
        .all()
    )

    total_sessions    = len(sessions)
    completed_sessions = sum(1 for s in sessions if s.completed)
    total_minutes     = sum(s.duration_min for s in sessions)
    xp_earned         = completed_sessions * 0  # calculé via XPLog

    # XP réels depuis XPLog pour être cohérent
    xp_focus = (
        db.query(func.sum(XPLog.xp_delta))
        .filter(
            XPLog.source == "focus",
            XPLog.date == today,
        )
        .scalar()
        or 0
    )

    return {
        "total_sessions":     total_sessions,
        "completed_sessions": completed_sessions,
        "total_minutes":      total_minutes,
        "xp_earned":          int(xp_focus),
    }


def get_focus_stats_by_pillar(db: Session) -> list[dict]:
    """
    Minutes de focus par pilier (tous temps).
    Utilisé par le skill tree pour débloquer des nœuds.
    """
    rows = (
        db.query(
            FocusSession.pillar_id,
            func.sum(FocusSession.duration_min).label("total_minutes"),
            func.count(FocusSession.id).label("total_sessions"),
        )
        .filter(FocusSession.completed == 1, FocusSession.pillar_id.isnot(None))
        .group_by(FocusSession.pillar_id)
        .all()
    )

    return [
        {
            "pillar_id":      row.pillar_id,
            "total_minutes":  int(row.total_minutes or 0),
            "total_sessions": int(row.total_sessions or 0),
        }
        for row in rows
    ]


def get_focus_minutes_for_pillar(db: Session, pillar_id: int) -> int:
    """Minutes de focus complétées pour un pilier donné (tous temps)."""
    result = (
        db.query(func.sum(FocusSession.duration_min))
        .filter(
            FocusSession.pillar_id == pillar_id,
            FocusSession.completed == 1,
        )
        .scalar()
    )
    return int(result or 0)