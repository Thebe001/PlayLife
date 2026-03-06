from sqlalchemy.orm import Session
from datetime import date as DateType

from app.models.journal_entry import JournalEntry


def create_journal(db: Session, data) -> JournalEntry:
    entry = JournalEntry(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_journals(db: Session, limit: int = 100) -> list[JournalEntry]:
    # FIX: ancienne version sans ordre ni limite
    # → résultats aléatoires et potentiellement très longs
    return (
        db.query(JournalEntry)
        .order_by(JournalEntry.date.desc())
        .limit(limit)
        .all()
    )


def get_journal_by_date(db: Session, target_date: DateType) -> JournalEntry | None:
    """Récupère l'entrée du journal pour un jour précis."""
    return (
        db.query(JournalEntry)
        .filter(JournalEntry.date == target_date)
        .first()
    )


def update_journal(db: Session, entry_id: int, data: dict) -> JournalEntry | None:
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry


def delete_journal(db: Session, entry_id: int) -> bool:
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        return False
    db.delete(entry)
    db.commit()
    return True