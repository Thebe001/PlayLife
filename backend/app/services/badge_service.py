from sqlalchemy.orm import Session
from app.models.badge import Badge
from app.models.badge_unlock import BadgeUnlock
from app.models.xp_log import XPLog


def check_badges(db: Session):

    xp_logs = db.query(XPLog).count()

    badges = db.query(Badge).all()

    unlocked = []

    for badge in badges:

        if "first_action" in badge.condition_json and xp_logs >= 1:

            unlock = BadgeUnlock(badge_id=badge.id)

            db.add(unlock)

            unlocked.append(badge.name)

    db.commit()

    return unlocked