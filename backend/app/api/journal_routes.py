from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.journal_schema import JournalCreate, JournalUpdate, JournalResponse
from app.services.journal_service import create_journal, get_journals, update_journal, delete_journal

router = APIRouter(prefix="/journal", tags=["Journal"])


@router.post("/", response_model=JournalResponse)
def create_entry(data: JournalCreate, db: Session = Depends(get_db)):
    return create_journal(db, data)


@router.get("/", response_model=list[JournalResponse])
def read_entries(db: Session = Depends(get_db)):
    return get_journals(db)


@router.put("/{entry_id}", response_model=JournalResponse)
def update_entry(entry_id: int, data: JournalUpdate, db: Session = Depends(get_db)):
    entry = update_journal(db, entry_id, data.model_dump(exclude_none=True))
    if not entry:
        raise HTTPException(status_code=404, detail="Entrée introuvable")
    return entry


@router.delete("/{entry_id}")
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    success = delete_journal(db, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entrée introuvable")
    return {"message": "Entrée supprimée ✓"}