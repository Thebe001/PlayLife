from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.habit_schema import HabitCreate, HabitResponse
from app.services.habit_service import create_habit, get_habits, check_habit

router = APIRouter(prefix="/habits", tags=["Habits"])


@router.post("/", response_model=HabitResponse)
def create_new_habit(
    habit: HabitCreate,
    db: Session = Depends(get_db)
):

    return create_habit(db, habit)


@router.get("/", response_model=list[HabitResponse])
def read_habits(db: Session = Depends(get_db)):

    return get_habits(db)


@router.post("/check/{habit_id}")
def check_habit_action(
    habit_id: int,
    db: Session = Depends(get_db)
):

    return check_habit(db, habit_id)