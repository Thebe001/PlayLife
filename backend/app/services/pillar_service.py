from sqlalchemy.orm import Session
from app.models.pillar import Pillar


def create_pillar(db: Session, pillar_data) -> Pillar:
    pillar = Pillar(**pillar_data.model_dump())
    db.add(pillar)
    db.commit()
    db.refresh(pillar)
    return pillar


def get_pillars(db: Session) -> list[Pillar]:
    # FIX: ancienne version retournait TOUS les piliers y compris archivés
    return (
        db.query(Pillar)
        .filter(Pillar.is_active == True)
        .order_by(Pillar.id.asc())
        .all()
    )


def get_pillar_by_id(db: Session, pillar_id: int) -> Pillar | None:
    return db.query(Pillar).filter(Pillar.id == pillar_id).first()


def update_pillar(db: Session, pillar_id: int, data: dict) -> Pillar | None:
    pillar = db.query(Pillar).filter(Pillar.id == pillar_id).first()
    if not pillar:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(pillar, key, value)
    db.commit()
    db.refresh(pillar)
    return pillar


def archive_pillar(db: Session, pillar_id: int) -> bool:
    """Soft delete — conserve l'historique des scores."""
    pillar = db.query(Pillar).filter(Pillar.id == pillar_id).first()
    if not pillar:
        return False
    pillar.is_active = False
    db.commit()
    return True