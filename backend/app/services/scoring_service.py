from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import date

from app.models.habit_log import HabitLog
from app.models.habit import Habit
from app.models.daily_score import DailyScore
from app.models.global_score import GlobalScore
from app.models.pillar import Pillar
from app.models.xp_log import XPLog


def calculate_daily_scores(db: Session, target_date: date = None):
    """Calcule le score de chaque pilier pour une journée donnée."""

    target_date = target_date or date.today()

    # Récupérer tous les logs du jour avec le pilier associé via la habit
    logs = (
        db.query(HabitLog, Habit)
        .join(Habit, HabitLog.habit_id == Habit.id)
        .filter(HabitLog.date == target_date)
        .all()
    )

    # Agréger points par pilier
    pillar_points: dict[int, float] = {}
    pillar_max: dict[int, float] = {}

    for log, habit in logs:
        pid = habit.pillar_id
        if pid not in pillar_points:
            pillar_points[pid] = 0.0
            pillar_max[pid] = 0.0
        pillar_points[pid] += log.points_earned
        pillar_max[pid] += abs(habit.points)

    results = []

    for pillar_id, points in pillar_points.items():
        max_pts = pillar_max.get(pillar_id, 100)
        if max_pts == 0:
            max_pts = 100

        score_pct = round((points / max_pts) * 100, 2)
        score_pct = max(0.0, min(100.0, score_pct))  # clamp 0-100

        # Upsert : éviter les doublons si on recalcule
        existing = (
            db.query(DailyScore)
            .filter(
                DailyScore.date == target_date,
                DailyScore.pillar_id == pillar_id,
            )
            .first()
        )
        if existing:
            existing.score_pct = score_pct
            existing.points_earned = points
            existing.points_max = max_pts
            results.append(existing)
        else:
            score = DailyScore(
                date=target_date,
                pillar_id=pillar_id,
                score_pct=score_pct,
                points_earned=points,
                points_max=max_pts,
            )
            db.add(score)
            results.append(score)

    db.commit()
    return results


def calculate_global_score(db: Session, target_date: date = None):
    """Calcule le score global pondéré pour une journée."""

    target_date = target_date or date.today()

    scores = (
        db.query(DailyScore)
        .filter(DailyScore.date == target_date)
        .all()
    )

    if not scores:
        return {"date": str(target_date), "score_global": 0, "xp_earned": 0}

    total_weight = 0.0
    weighted_sum = 0.0

    for score in scores:
        pillar = db.query(Pillar).filter(Pillar.id == score.pillar_id).first()
        # ✅ Protection si pilier supprimé entre temps
        if not pillar or not pillar.is_active:
            continue
        weighted_sum += score.score_pct * (pillar.weight_pct / 100)
        total_weight += pillar.weight_pct / 100

    # Normaliser si les poids ne font pas exactement 100%
    if total_weight > 0:
        global_score_value = round(weighted_sum / total_weight, 2)
    else:
        global_score_value = 0.0

    xp_earned = int(global_score_value)

    # Upsert
    existing = (
        db.query(GlobalScore)
        .filter(GlobalScore.date == target_date)
        .first()
    )
    if existing:
        existing.score_global = global_score_value
        existing.xp_earned = xp_earned
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


def get_today_summary(db: Session):
    """Retourne un résumé complet du jour : scores par pilier + score global + XP réel."""

    today = date.today()

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

    # ✅ Fix : XP du jour depuis XPLog (vrais points gagnés aujourd'hui)
    xp_today = (
        db.query(func.sum(XPLog.xp_delta))
        .filter(XPLog.date == today)
        .scalar()
        or 0
    )

    return {
        "date": str(today),
        "global_score": global_score.score_global if global_score else 0,
        "xp_today": int(xp_today),
        "pillars": [
            {
                "pillar_id": pillar.id,
                "pillar_name": pillar.name,
                "pillar_color": pillar.color,
                "score_pct": ds.score_pct,
                "points_earned": ds.points_earned,
                "points_max": ds.points_max,
            }
            for ds, pillar in daily_scores
        ],
    }