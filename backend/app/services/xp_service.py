from sqlalchemy.orm import Session
from app.models.xp_log import XPLog
from app.models.level import Level


def add_xp(db: Session, xp: int, source: str):

    log = XPLog(
        xp_delta=xp,
        source=source,
        description=f"XP from {source}"
    )

    db.add(log)
    db.commit()

    return log


def get_total_xp(db: Session):

    logs = db.query(XPLog).all()

    total = sum(log.xp_delta for log in logs)

    return total


def get_current_level(db: Session):

    total_xp = get_total_xp(db)

    levels = db.query(Level).all()

    for level in levels:

        if level.min_xp <= total_xp <= level.max_xp:
            return level

    return None