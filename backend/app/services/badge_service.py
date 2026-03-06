from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.models.badge import Badge
from app.models.badge_unlock import BadgeUnlock
from app.models.habit_log import HabitLog
from app.models.global_score import GlobalScore


def check_badges(db: Session):
    badges = db.query(Badge).all()
    already_unlocked = {bu.badge_id for bu in db.query(BadgeUnlock).all()}
    unlocked = []

    total_xp_logs = db.query(HabitLog).count()
    streak = get_global_streak(db)
    scores = db.query(GlobalScore).order_by(GlobalScore.date.desc()).all()

    for badge in badges:
        if badge.id in already_unlocked:
            continue

        condition = badge.condition_json or ""
        should_unlock = False

        if "first_action" in condition and total_xp_logs >= 1:
            should_unlock = True
        elif "streak_7" in condition and streak >= 7:
            should_unlock = True
        elif "streak_100" in condition and streak >= 100:
            should_unlock = True
        elif "perfect_week" in condition:
            last_7 = scores[:7]
            if len(last_7) == 7 and all(s.score_global >= 95 for s in last_7):
                should_unlock = True
        elif "diamond_month" in condition:
            last_30 = scores[:30]
            if len(last_30) == 30 and all(s.score_global >= 90 for s in last_30):
                should_unlock = True

        if should_unlock:
            unlock = BadgeUnlock(badge_id=badge.id)
            db.add(unlock)
            unlocked.append(badge.name)

    db.commit()
    return unlocked


def get_global_streak(db: Session) -> int:
    scores = (
        db.query(GlobalScore)
        .order_by(GlobalScore.date.desc())
        .all()
    )

    if not scores:
        return 0

    streak = 0
    check_date = date.today()

    for score in scores:
        if score.date == check_date and score.score_global > 0:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    return streak


def get_unlocked_badges(db: Session):
    unlocks = db.query(BadgeUnlock).all()
    seen_badge_ids = set()
    result = []

    for unlock in unlocks:
        if unlock.badge_id in seen_badge_ids:
            continue
        seen_badge_ids.add(unlock.badge_id)
        badge = db.query(Badge).filter(Badge.id == unlock.badge_id).first()
        if badge:
            result.append({
                "id": badge.id,
                "name": badge.name,
                "icon": badge.icon,
                "description": badge.description,
                "unlocked_at": unlock.unlocked_at,
            })

    return result