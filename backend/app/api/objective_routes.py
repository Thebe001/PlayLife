from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db import get_db
from app.models.objective import Objective
from app.models.task import Task
from app.schemas.objective_schema import ObjectiveCreate, ObjectiveUpdate, TaskCreate
from app.services.xp_service import add_xp
from app.services.scoring_service import calculate_daily_scores, calculate_global_score
from datetime import date

router = APIRouter(prefix="/objectives", tags=["Objectives"])

# ── Constante XP bonus objectif complété (cahier des charges : +100 pts) ──
_OBJECTIVE_COMPLETION_BONUS_XP = 100


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


# ── Tasks ──────────────────────────────────────────────────────────────────

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

    # Idempotent : ignorer si déjà complétée
    if task.status == "done":
        return {
            "message": "Tâche déjà complétée",
            "xp_earned": 0,
            "objective_completed": False,
        }

    task.status = "done"
    db.commit()

    # ── XP pour la tâche (points de la tâche → XP) ────────────────────────
    xp_earned = 0
    if task.points and task.points > 0:
        add_xp(db, task.points, source="task")
        xp_earned += task.points

    # ── Recalcul completion_pct de l'objectif parent ──────────────────────
    objective_completed = False
    if task.objective_id:
        all_tasks = db.query(Task).filter(Task.objective_id == task.objective_id).all()
        done_count = sum(1 for t in all_tasks if t.status == "done")
        pct = round((done_count / len(all_tasks)) * 100, 1) if all_tasks else 0.0

        obj = db.query(Objective).filter(Objective.id == task.objective_id).first()
        if obj:
            obj.completion_pct = pct
            if pct == 100.0 and obj.status != "completed":
                obj.status = "completed"
                objective_completed = True
                # Bonus XP objectif complété (+100 pts — cahier des charges)
                add_xp(db, _OBJECTIVE_COMPLETION_BONUS_XP, source="objective")
                xp_earned += _OBJECTIVE_COMPLETION_BONUS_XP
            db.commit()

    # ── Recalcul scores globaux du jour ───────────────────────────────────
    # (les tâches n'ont pas de pillar_score direct mais l'XP impacte la gamification)
    calculate_daily_scores(db)
    calculate_global_score(db)

    return {
        "message": "Tâche complétée ✓",
        "points": task.points,
        "xp_earned": xp_earned,
        "objective_completed": objective_completed,
    }