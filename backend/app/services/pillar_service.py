from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.pillar import Pillar


# Seuil de tolérance pour la somme des poids (flottants)
_WEIGHT_TOLERANCE = 0.01


def _get_active_weight_sum(db: Session, exclude_id: int | None = None) -> float:
    """Calcule la somme des poids des piliers actifs, en excluant optionnellement un pilier."""
    query = db.query(Pillar).filter(Pillar.is_active == True)
    if exclude_id:
        query = query.filter(Pillar.id != exclude_id)
    pillars = query.all()
    return sum(p.weight_pct for p in pillars)


def validate_weight_budget(
    db: Session,
    new_weight: float,
    exclude_id: int | None = None,
) -> None:
    """
    Lève HTTP 422 si l'ajout du nouveau poids ferait dépasser 100%.
    On autorise jusqu'à 100% exactement, pas plus.
    """
    current_sum = _get_active_weight_sum(db, exclude_id=exclude_id)
    if current_sum + new_weight > 100 + _WEIGHT_TOLERANCE:
        remaining = round(100 - current_sum, 2)
        raise HTTPException(
            status_code=422,
            detail=(
                f"Les poids dépasseraient 100% "
                f"(actuel : {round(current_sum, 2)}%, "
                f"ajout : {new_weight}%, "
                f"budget restant : {remaining}%)"
            ),
        )


def create_pillar(db: Session, pillar_data) -> Pillar:
    validate_weight_budget(db, pillar_data.weight_pct)
    pillar = Pillar(**pillar_data.model_dump())
    db.add(pillar)
    db.commit()
    db.refresh(pillar)
    return pillar


def get_pillars(db: Session) -> list[Pillar]:
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
    # Si on modifie le poids, valider le budget en excluant le pilier lui-même
    if "weight_pct" in data:
        validate_weight_budget(db, data["weight_pct"], exclude_id=pillar_id)
    for key, value in data.items():
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


def get_weight_summary(db: Session) -> dict:
    """Retourne la somme des poids et le budget restant — utilisé par le frontend."""
    total = _get_active_weight_sum(db)
    return {
        "total_weight": round(total, 2),
        "remaining":    round(100 - total, 2),
        "is_valid":     abs(total - 100) <= _WEIGHT_TOLERANCE,
    }