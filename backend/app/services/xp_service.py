from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.xp_log import XPLog
from app.models.level import Level


def add_xp(db: Session, xp: int, source: str) -> XPLog:
    """Ajoute des XP et les logue."""
    log = XPLog(
        xp_delta=xp,
        source=source,
        description=f"XP from {source}",
    )
    db.add(log)
    db.commit()
    return log


def get_total_xp(db: Session) -> int:
    """
    FIX: était db.query(XPLog).all() puis sum() Python
    → charge tous les logs en mémoire inutilement.
    Maintenant : une seule requête SQL avec func.sum().
    """
    result = db.query(func.sum(XPLog.xp_delta)).scalar()
    return int(result or 0)


def get_current_level(db: Session) -> Level | None:
    """
    Retourne le niveau correspondant au XP total.
    FIX: charge tous les levels en mémoire — OK car peu de lignes,
    mais on trie maintenant par min_xp DESC pour prendre le bon niveau
    même si les plages ne se chevauchent pas parfaitement.
    """
    total_xp = get_total_xp(db)

    # Prendre le niveau le plus haut dont min_xp <= total_xp
    level = (
        db.query(Level)
        .filter(Level.min_xp <= total_xp)
        .order_by(Level.min_xp.desc())
        .first()
    )
    return level