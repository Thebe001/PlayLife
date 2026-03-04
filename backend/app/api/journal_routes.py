from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.journal_schema import JournalCreate, JournalResponse
from app.services.journal_service import create_journal, get_journals

router = APIRouter(prefix="/journal", tags=["Journal"])


@router.post("/", response_model=JournalResponse)
def create_entry(data: JournalCreate, db: Session = Depends(get_db)):

    return create_journal(db, data)


@router.get("/", response_model=list[JournalResponse])
def read_entries(db: Session = Depends(get_db)):

    return get_journals(db)