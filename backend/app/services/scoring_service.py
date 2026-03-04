from sqlalchemy.orm import Session
from datetime import date

from app.models.habit_log import HabitLog
from app.models.daily_score import DailyScore
from app.models.global_score import GlobalScore
from app.models.pillar import Pillar


def calculate_daily_scores(db: Session):

    today = date.today()

    logs = db.query(HabitLog).filter(HabitLog.date == today).all()

    pillar_points = {}

    for log in logs:

        if log.habit_id not in pillar_points:

            pillar_points[log.habit_id] = 0

        pillar_points[log.habit_id] += log.points_earned

    results = []

    for pillar_id, points in pillar_points.items():

        score = DailyScore(
            pillar_id=pillar_id,
            score_pct=points,
            points_earned=points,
            points_max=100
        )

        db.add(score)

        results.append(score)

    db.commit()

    return results


def calculate_global_score(db: Session):

    today = date.today()

    scores = db.query(DailyScore).filter(DailyScore.date == today).all()

    total = 0

    for score in scores:

        pillar = db.query(Pillar).filter(Pillar.id == score.pillar_id).first()

        total += score.score_pct * pillar.weight_pct / 100

    global_score = GlobalScore(
        score_global=total,
        xp_earned=int(total)
    )

    db.add(global_score)

    db.commit()

    return global_score