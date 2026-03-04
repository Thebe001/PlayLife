from sqlalchemy.orm import Session
from app.models.journal_entry import JournalEntry


def create_journal(db: Session, data):

    entry = JournalEntry(**data.dict())

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return entry


def get_journals(db: Session):

    return db.query(JournalEntry).all()