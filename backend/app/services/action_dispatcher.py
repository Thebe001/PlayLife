from sqlalchemy.orm import Session
from datetime import date

from app.models.habit import Habit
from app.models.objective import Objective
from app.models.pillar import Pillar
from app.services.habit_service import check_habit
from app.services.xp_service import add_xp
from app.services.scoring_service import calculate_daily_scores, calculate_global_score, get_today_summary


def dispatch(action: str, params: dict, db: Session) -> dict:
    """Exécute l'action détectée par le LLM."""

    if action == "check_habit":
        return _check_habit(params, db)

    elif action == "get_score":
        return _get_score(db)

    elif action == "create_objective":
        return _create_objective(params, db)

    elif action == "create_habit":
        return _create_habit(params, db)

    elif action == "get_objectives":
        return _get_objectives(db)

    elif action == "add_journal":
        return {"status": "redirect", "page": "/dashboard/journal", "data": params}

    elif action == "generate_review":
        return {"status": "redirect", "page": "/dashboard/reviews"}

    else:
        return {"status": "unknown", "message": "Action non reconnue"}


def _check_habit(params: dict, db: Session) -> dict:
    habit_name = params.get("habit_name", "").lower()
    habits = db.query(Habit).filter(Habit.is_active == True).all()

    # Fuzzy match par nom
    match = None
    for h in habits:
        if habit_name in h.name.lower() or h.name.lower() in habit_name:
            match = h
            break

    if not match:
        return {
            "status": "error",
            "message": f"Habitude '{habit_name}' introuvable. Habitudes disponibles : {[h.name for h in habits]}"
        }

    result = check_habit(db, match.id)
    if "points_earned" in result and result["points_earned"] > 0:
        add_xp(db, result["points_earned"], "habit_voice")
    calculate_daily_scores(db)
    calculate_global_score(db)

    return {"status": "success", "habit": match.name, "points": result.get("points_earned", 0)}


def _get_score(db: Session) -> dict:
    summary = get_today_summary(db)
    return {"status": "success", "summary": summary}


def _create_objective(params: dict, db: Session) -> dict:
    pillar_name = params.get("pillar", "").lower()
    pillars = db.query(Pillar).filter(Pillar.is_active == True).all()

    pillar = None
    for p in pillars:
        if pillar_name in p.name.lower():
            pillar = p
            break

    if not pillar and pillars:
        pillar = pillars[0]

    obj = Objective(
        pillar_id=pillar.id if pillar else 1,
        title=params.get("title", "Nouvel objectif"),
        horizon=params.get("horizon", "monthly"),
        deadline=params.get("deadline"),
        completion_pct=0,
        status="active",
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)

    return {"status": "success", "objective_id": obj.id, "title": obj.title}


def _create_habit(params: dict, db: Session) -> dict:
    pillar_name = params.get("pillar", "").lower()
    pillars = db.query(Pillar).filter(Pillar.is_active == True).all()

    pillar = None
    for p in pillars:
        if pillar_name in p.name.lower():
            pillar = p
            break

    if not pillar and pillars:
        pillar = pillars[0]

    from app.models.habit import Habit
    habit = Habit(
        pillar_id=pillar.id if pillar else 1,
        name=params.get("name", "Nouvelle habitude"),
        type=params.get("type", "good"),
        points=int(params.get("points", 20)),
        frequency="daily",
        is_active=True,
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)

    return {"status": "success", "habit_id": habit.id, "name": habit.name}


def _get_objectives(db: Session) -> dict:
    objs = db.query(Objective).filter(Objective.status == "active").all()
    return {
        "status": "success",
        "objectives": [{"id": o.id, "title": o.title, "completion": o.completion_pct} for o in objs]
    }