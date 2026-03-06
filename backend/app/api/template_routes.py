from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.template_schema import TemplateCreate, TemplateResponse
from app.services.template_service import create_template, get_templates
from app.models.day_template import DayTemplate

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.get("/", response_model=list[TemplateResponse])
def read_templates(db: Session = Depends(get_db)):
    return get_templates(db)


@router.post("/", response_model=TemplateResponse)
def create_template_api(data: TemplateCreate, db: Session = Depends(get_db)):
    return create_template(db, data)


@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(DayTemplate).filter(DayTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template introuvable")
    db.delete(template)
    db.commit()
    return {"message": "Template supprimé ✓"}