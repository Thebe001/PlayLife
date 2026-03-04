from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.review_schema import ReviewCreate, ReviewResponse
from app.services.review_service import create_review, get_reviews

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse)
def create_review_api(data: ReviewCreate, db: Session = Depends(get_db)):

    return create_review(db, data)


@router.get("/", response_model=list[ReviewResponse])
def read_reviews(db: Session = Depends(get_db)):

    return get_reviews(db)