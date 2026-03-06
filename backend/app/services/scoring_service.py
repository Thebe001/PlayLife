from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import date

from app.models.habit_log import HabitLog
from app.models.habit import Habit
from app.models.daily_score import DailyScore
from app.models.global_score import GlobalScore
from app.models.pillar import Pillar
from app.models.xp_log import XPLog


def calculate_daily_scores(db: Session, target_date: date = None) -> list:
    """Calcule le score de chaque pilier pour une journée donnée."""

    target_date = target_date or date.today()

    # Un seul JOIN HabitLog → Habit pour récupérer tous les logs du jour
    logs = (
        db.query(HabitLog, Habit)
        .join(Habit, HabitLog.habit_id == Habit.id)
        .filter(HabitLog.date == target_date)
        .all()
    )

    # Agréger points et max par pilier en Python (évite N requêtes)
    pillar_points: dict[int, float] = {}
    pillar_max:    dict[int, float] = {}

    for log, habit in logs:
        pid = habit.pillar_id
        if pid not in pillar_points:
            pillar_points[pid] = 0.0
            pillar_max[pid]    = 0.0
        pillar_points[pid] += log.points_earned
        pillar_max[pid]    += abs(habit.points)

    # Charger les DailyScore existants en une seule requête (évite N upserts séparés)
    existing_scores: dict[int, DailyScore] = {
        ds.pillar_id: ds
        for ds in db.query(DailyScore)
        .filter(
            DailyScore.date == target_date,
            DailyScore.pillar_id.in_(list(pillar_points.keys())),
        )
        .all()
    }

    results = []

    for pillar_id, points in pillar_points.items():
        max_pts = pillar_max.get(pillar_id, 100) or 100

        score_pct = round((points / max_pts) * 100, 2)
        score_pct = max(0.0, min(100.0, score_pct))  # clamp 0–100

        if pillar_id in existing_scores:
            # Upsert — mise à jour de la ligne existante
            ds = existing_scores[pillar_id]
            ds.score_pct     = score_pct
            ds.points_earned = points
            ds.points_max    = max_pts
            results.append(ds)
        else:
            ds = DailyScore(
                date=target_date,
                pillar_id=pillar_id,
                score_pct=score_pct,
                points_earned=points,
                points_max=max_pts,
            )
            db.add(ds)
            results.append(ds)

    db.commit()
    return results


def calculate_global_score(db: Session, target_date: date = None):
    """
    Calcule le score global pondéré pour une journée.

    FIX: ancienne version faisait une requête DB par pilier dans la boucle (N+1).
    Maintenant : un seul JOIN DailyScore → Pillar.
    """

    target_date = target_date or date.today()

    # Un seul JOIN pour récupérer les scores ET les poids des piliers
    rows = (
        db.query(DailyScore, Pillar)
        .join(Pillar, DailyScore.pillar_id == Pillar.id)
        .filter(
            DailyScore.date == target_date,
            Pillar.is_active == True,
        )
        .all()
    )

    if not rows:
        return {"date": str(target_date), "score_global": 0, "xp_earned": 0}

    weighted_sum = 0.0
    total_weight = 0.0

    for daily_score, pillar in rows:
        w = pillar.weight_pct / 100
        weighted_sum += daily_score.score_pct * w
        total_weight += w

    # Normaliser si les poids ne font pas exactement 100%
    global_score_value = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0.0
    xp_earned = int(global_score_value)

    # Upsert GlobalScore
    existing = (
        db.query(GlobalScore)
        .filter(GlobalScore.date == target_date)
        .first()
    )
    if existing:
        existing.score_global = global_score_value
        existing.xp_earned    = xp_earned
        result = existing
    else:
        result = GlobalScore(
            date=target_date,
            score_global=global_score_value,
            xp_earned=xp_earned,
        )
        db.add(result)

    db.commit()
    return result


def get_today_summary(db: Session) -> dict:
    """Résumé complet du jour : scores par pilier + score global + XP réel."""

    today = date.today()

    # JOIN DailyScore → Pillar en une requête
    daily_scores = (
        db.query(DailyScore, Pillar)
        .join(Pillar, DailyScore.pillar_id == Pillar.id)
        .filter(DailyScore.date == today)
        .all()
    )

    global_score = (
        db.query(GlobalScore)
        .filter(GlobalScore.date == today)
        .first()
    )

    # XP du jour via func.sum — une seule requête SQL
    xp_today = (
        db.query(func.sum(XPLog.xp_delta))
        .filter(XPLog.date == today)
        .scalar()
        or 0
    )

    return {
        "date":         str(today),
        "global_score": global_score.score_global if global_score else 0,
        "xp_today":     int(xp_today),
        "pillars": [
            {
                "pillar_id":     pillar.id,
                "pillar_name":   pillar.name,
                "pillar_color":  pillar.color,
                "score_pct":     ds.score_pct,
                "points_earned": ds.points_earned,
                "points_max":    ds.points_max,
            }
            for ds, pillar in daily_scores
        ],
    }