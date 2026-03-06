from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db import get_db
from app.models.objective import Objective
from app.models.task import Task
from app.schemas.objective_schema import ObjectiveCreate, ObjectiveUpdate, TaskCreate
from datetime import date

router = APIRouter(prefix="/objectives", tags=["Objectives"])


@router.post("/")
def create_objective(data: ObjectiveCreate, db: Session = Depends(get_db)):
    obj = Objective(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/")
def list_objectives(
    horizon: Optional[str] = None,
    status: Optional[str] = None,
    pillar_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Objective)
    if horizon:
        query = query.filter(Objective.horizon == horizon)
    if status:
        query = query.filter(Objective.status == status)
    if pillar_id:
        query = query.filter(Objective.pillar_id == pillar_id)
    return query.all()


@router.get("/{obj_id}")
def get_objective(obj_id: int, db: Session = Depends(get_db)):
    obj = db.query(Objective).filter(Objective.id == obj_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Objectif introuvable")
    tasks = db.query(Task).filter(Task.objective_id == obj_id).all()
    return {**obj.__dict__, "tasks": tasks}


@router.put("/{obj_id}")
def update_objective(obj_id: int, data: ObjectiveUpdate, db: Session = Depends(get_db)):
    obj = db.query(Objective).filter(Objective.id == obj_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Objectif introuvable")
    for key, val in data.model_dump(exclude_none=True).items():
        setattr(obj, key, val)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{obj_id}")
def delete_objective(obj_id: int, db: Session = Depends(get_db)):
    obj = db.query(Objective).filter(Objective.id == obj_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Objectif introuvable")
    db.delete(obj)
    db.commit()
    return {"message": "Objectif supprimé"}


# ── Tasks ──────────────────────────────────────────────

@router.post("/tasks/")
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks/today")
def get_tasks_today(db: Session = Depends(get_db)):
    today = date.today()
    return (
        db.query(Task)
        .filter(Task.due_date == today, Task.status != "done")
        .all()
    )


@router.patch("/tasks/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tâche introuvable")

    task.status = "done"
    db.commit()

    # Recalculer completion_pct de l'objectif parent
    if task.objective_id:
        all_tasks = db.query(Task).filter(Task.objective_id == task.objective_id).all()
        done = sum(1 for t in all_tasks if t.status == "done")
        pct = round((done / len(all_tasks)) * 100, 1) if all_tasks else 0
        obj = db.query(Objective).filter(Objective.id == task.objective_id).first()
        if obj:
            obj.completion_pct = pct
            if pct == 100:
                obj.status = "completed"
            db.commit()

    return {"message": "Tâche complétée ✓", "points": task.points}