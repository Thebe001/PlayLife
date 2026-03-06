from sqlalchemy.orm import Session
from app.models.day_template import DayTemplate


def create_template(db: Session, data):

    template = DayTemplate(**data.model_dump())

    db.add(template)
    db.commit()
    db.refresh(template)

    return template


def get_templates(db: Session):

    return db.query(DayTemplate).all()