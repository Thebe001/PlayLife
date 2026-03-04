from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.template_schema import TemplateCreate, TemplateResponse
from app.services.template_service import create_template, get_templates

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.post("/", response_model=TemplateResponse)
def create_template_api(data: TemplateCreate, db: Session = Depends(get_db)):

    return create_template(db, data)


@router.get("/", response_model=list[TemplateResponse])
def read_templates(db: Session = Depends(get_db)):

    return get_templates(db)