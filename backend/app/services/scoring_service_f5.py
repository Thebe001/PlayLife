"""
scoring_service.py — mis à jour pour Feature 5
Après chaque calculate_global_score(), on vérifie automatiquement les sanctions.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import date

from app.models.habit_log import HabitLog
from app.models.habit import Habit
from app.models.daily_score import DailyScore
from app.models.global_score import GlobalScore
from app.models.pillar import Pillar
from app.models.xp_log import XPLog


def calculate_daily_scores(db: Session, target_date: date = None) -> list[DailyScore]:
    """
    Calcule les scores par pilier pour une date donnée (défaut : aujourd'hui).

    Formule : score_pilier = (points_earned / points_max) × 100, clampé 0–100.
    Pondération normalisée sur les piliers actifs.
    Upsert : met à jour si un score existe déjà pour ce pilier/date.
    """
    if target_date is None:
        target_date = date.today()

    pillars = db.query(Pillar).filter(Pillar.is_active == True).all()
    results = []

    for pillar in pillars:
        habits = (
            db.query(Habit)
            .filter(Habit.pillar_id == pillar.id, Habit.is_active == True)
            .all()
        )

        if not habits:
            continue

        habit_ids  = [h.id for h in habits]
        points_max = sum(abs(h.points) for h in habits if h.type == "good")

        if points_max == 0:
            continue

        points_earned = (
            db.query(func.sum(HabitLog.points_earned))
            .filter(
                HabitLog.habit_id.in_(habit_ids),
                HabitLog.date == target_date,
                HabitLog.checked == True,
            )
            .scalar()
            or 0
        )

        score_pct = round(min(max((points_earned / points_max) * 100, 0), 100), 2)

        existing = (
            db.query(DailyScore)
            .filter(DailyScore.pillar_id == pillar.id, DailyScore.date == target_date)
            .first()
        )

        if existing:
            existing.score_pct     = score_pct
            existing.points_earned = points_earned
            existing.points_max    = points_max
            results.append(existing)
        else:
            ds = DailyScore(
                pillar_id=pillar.id,
                date=target_date,
                score_pct=score_pct,
                points_earned=points_earned,
                points_max=points_max,
            )
            db.add(ds)
            results.append(ds)

    db.commit()
    return results


def calculate_global_score(db: Session, target_date: date = None) -> GlobalScore:
    """
    Calcule le score global pondéré pour une date donnée (défaut : aujourd'hui).

    Formule : score_global = Σ (score_pilier × weight_pct) / Σ weight_pct
    Upsert + XP log + déclenchement automatique des sanctions.
    """
    if target_date is None:
        target_date = date.today()

    daily_scores = (
        db.query(DailyScore, Pillar)
        .join(Pillar, DailyScore.pillar_id == Pillar.id)
        .filter(DailyScore.date == target_date, Pillar.is_active == True)
        .all()
    )

    if not daily_scores:
        score_global = 0.0
    else:
        total_weight   = sum(p.weight_pct for _, p in daily_scores)
        weighted_sum   = sum(ds.score_pct * p.weight_pct for ds, p in daily_scores)
        score_global   = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0.0

    xp_earned = int(score_global)

    existing = (
        db.query(GlobalScore)
        .filter(GlobalScore.date == target_date)
        .first()
    )

    if existing:
        existing.score_global = score_global
        existing.xp_earned    = xp_earned
    else:
        gs = GlobalScore(
            date=target_date,
            score_global=score_global,
            xp_earned=xp_earned,
        )
        db.add(gs)

    db.commit()

    # ── Auto-trigger sanctions ─────────────────────────────────────────────
    # Import local pour éviter la dépendance circulaire
    from app.services.sanction_service import check_and_trigger_sanctions
    check_and_trigger_sanctions(db)
    # ──────────────────────────────────────────────────────────────────────

    return existing or db.query(GlobalScore).filter(GlobalScore.date == target_date).first()


def get_today_summary(db: Session) -> dict:
    """
    Résumé du jour : score global, XP, détail par pilier.
    Utilisé par le dashboard.
    """
    today = date.today()

    global_score = (
        db.query(GlobalScore)
        .filter(GlobalScore.date == today)
        .first()
    )

    daily_scores = (
        db.query(DailyScore, Pillar)
        .join(Pillar, DailyScore.pillar_id == Pillar.id)
        .filter(DailyScore.date == today)
        .all()
    )

    xp_today = (
        db.query(func.sum(XPLog.xp_delta))
        .filter(func.date(XPLog.created_at) == today)
        .scalar()
        or 0
    )

    return {
        "date":         today.isoformat(),
        "global_score": global_score.score_global if global_score else 0,
        "xp_today":     int(xp_today),
        "pillars": [
            {
                "pillar_id":    pillar.id,
                "pillar_name":  pillar.name,
                "pillar_color": pillar.color,
                "score_pct":    ds.score_pct,
                "points_earned": ds.points_earned,
                "points_max":   ds.points_max,
            }
            for ds, pillar in daily_scores
        ],
    }