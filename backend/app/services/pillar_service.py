from sqlalchemy.orm import Session
from app.models.pillar import Pillar


def create_pillar(db: Session, pillar_data):

    pillar = Pillar(**pillar_data.dict())

    db.add(pillar)
    db.commit()
    db.refresh(pillar)

    return pillar


def get_pillars(db: Session):

    return db.query(Pillar).all()