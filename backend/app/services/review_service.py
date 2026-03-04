from sqlalchemy.orm import Session
from app.models.review import Review


def create_review(db: Session, data):

    review = Review(**data.dict())

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


def get_reviews(db: Session):

    return db.query(Review).all()