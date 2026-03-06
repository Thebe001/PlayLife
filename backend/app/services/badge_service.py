from sqlalchemy.orm import Session, joinedload
from datetime import date, timedelta

from app.models.badge import Badge
from app.models.badge_unlock import BadgeUnlock
from app.models.habit_log import HabitLog
from app.models.global_score import GlobalScore


def check_badges(db: Session) -> list[str]:
    """
    Vérifie et débloque les badges mérités.
    FIX: ancienne version faisait des requêtes séparées par badge (N+1).
    Maintenant toutes les données sont chargées en amont.
    """
    # Charger tout en une seule fois
    badges = db.query(Badge).all()
    already_unlocked_ids = {
        bu.badge_id for bu in db.query(BadgeUnlock.badge_id).all()
    }

    total_habit_checks = db.query(HabitLog).filter(HabitLog.checked == True).count()
    streak = get_global_streak(db)
    scores = (
        db.query(GlobalScore)
        .order_by(GlobalScore.date.desc())
        .all()
    )

    unlocked = []

    for badge in badges:
        if badge.id in already_unlocked_ids:
            continue

        condition = badge.condition_json or ""
        should_unlock = False

        if "first_action" in condition and total_habit_checks >= 1:
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
            db.add(BadgeUnlock(badge_id=badge.id))
            unlocked.append(badge.name)

    if unlocked:
        db.commit()

    return unlocked


def get_global_streak(db: Session) -> int:
    """Retourne le streak global actuel (jours consécutifs avec score > 0)."""
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


def get_unlocked_badges(db: Session) -> list[dict]:
    """
    FIX: ancienne version faisait une requête DB par badge dans la boucle (N+1).
    Maintenant : un seul JOIN pour tout récupérer.
    """
    # Un seul JOIN BadgeUnlock → Badge
    rows = (
        db.query(BadgeUnlock, Badge)
        .join(Badge, BadgeUnlock.badge_id == Badge.id)
        .order_by(BadgeUnlock.unlocked_at.desc())
        .all()
    )

    seen = set()
    result = []

    for unlock, badge in rows:
        if badge.id in seen:
            continue
        seen.add(badge.id)
        result.append({
            "id":           badge.id,
            "name":         badge.name,
            "icon":         badge.icon,
            "description":  badge.description,
            "unlocked_at":  unlock.unlocked_at,
        })

    return result