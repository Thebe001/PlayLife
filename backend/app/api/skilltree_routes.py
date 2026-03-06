from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models.pillar import Pillar
from app.models.xp_log import XPLog
from app.models.habit_log import HabitLog
from app.models.habit import Habit
from app.models.objective import Objective

router = APIRouter(prefix="/skilltree", tags=["Skill Tree"])


def get_pillar_xp(db: Session, pillar_id: int) -> int:
    """XP gagné sur un pilier = somme des points des habitudes cochées de ce pilier."""
    result = (
        db.query(func.sum(HabitLog.points_earned))
        .join(Habit, HabitLog.habit_id == Habit.id)
        .filter(Habit.pillar_id == pillar_id, HabitLog.checked == True)
        .scalar()
    )
    return int(result or 0)


def get_pillar_stats(db: Session, pillar_id: int) -> dict:
    """Stats détaillées d'un pilier pour calculer les skills débloqués."""
    total_checks = (
        db.query(HabitLog)
        .join(Habit, HabitLog.habit_id == Habit.id)
        .filter(Habit.pillar_id == pillar_id, HabitLog.checked == True)
        .count()
    )
    completed_objectives = (
        db.query(Objective)
        .filter(Objective.pillar_id == pillar_id, Objective.status == "completed")
        .count()
    )
    return {
        "total_checks": total_checks,
        "completed_objectives": completed_objectives,
    }


SKILL_TREES = {
    "default": [
        # Niveau 1 — débloqué dès le début
        {
            "id": "starter",
            "label": "Premier Pas",
            "icon": "🌱",
            "description": "Tu as commencé ton parcours.",
            "xp_required": 0,
            "checks_required": 0,
            "tier": 1,
            "position": {"x": 0, "y": 0},
        },
        # Niveau 2
        {
            "id": "consistent",
            "label": "Consistance",
            "icon": "🔄",
            "description": "10 habitudes cochées sur ce pilier.",
            "xp_required": 50,
            "checks_required": 10,
            "tier": 2,
            "position": {"x": -1, "y": 1},
        },
        {
            "id": "focused",
            "label": "Focus",
            "icon": "🎯",
            "description": "100 XP gagnés sur ce pilier.",
            "xp_required": 100,
            "checks_required": 0,
            "tier": 2,
            "position": {"x": 1, "y": 1},
        },
        # Niveau 3
        {
            "id": "dedicated",
            "label": "Dédié",
            "icon": "💪",
            "description": "30 habitudes cochées sur ce pilier.",
            "xp_required": 150,
            "checks_required": 30,
            "tier": 3,
            "position": {"x": -2, "y": 2},
        },
        {
            "id": "achiever",
            "label": "Réalisateur",
            "icon": "🏆",
            "description": "1 objectif complété sur ce pilier.",
            "xp_required": 200,
            "checks_required": 0,
            "tier": 3,
            "position": {"x": 0, "y": 2},
            "objectives_required": 1,
        },
        {
            "id": "expert",
            "label": "Expert",
            "icon": "⭐",
            "description": "300 XP gagnés sur ce pilier.",
            "xp_required": 300,
            "checks_required": 0,
            "tier": 3,
            "position": {"x": 2, "y": 2},
        },
        # Niveau 4
        {
            "id": "master",
            "label": "Maître",
            "icon": "👑",
            "description": "100 habitudes cochées + 3 objectifs complétés.",
            "xp_required": 500,
            "checks_required": 100,
            "tier": 4,
            "position": {"x": -1, "y": 3},
            "objectives_required": 3,
        },
        {
            "id": "legend",
            "label": "Légende",
            "icon": "🌟",
            "description": "1000 XP gagnés sur ce pilier.",
            "xp_required": 1000,
            "checks_required": 0,
            "tier": 4,
            "position": {"x": 1, "y": 3},
        },
    ]
}


@router.get("/")
def get_skill_tree(db: Session = Depends(get_db)):
    """Retourne le skill tree complet pour tous les piliers."""
    pillars = db.query(Pillar).filter(Pillar.is_active == True).all()

    result = []
    for pillar in pillars:
        xp = get_pillar_xp(db, pillar.id)
        stats = get_pillar_stats(db, pillar.id)
        skills = SKILL_TREES["default"]

        unlocked_skills = []
        for skill in skills:
            xp_ok = xp >= skill["xp_required"]
            checks_ok = stats["total_checks"] >= skill.get("checks_required", 0)
            obj_ok = stats["completed_objectives"] >= skill.get("objectives_required", 0)
            unlocked = xp_ok and checks_ok and obj_ok

            unlocked_skills.append({
                **skill,
                "unlocked": unlocked,
                "progress": {
                    "xp_current": xp,
                    "xp_required": skill["xp_required"],
                    "checks_current": stats["total_checks"],
                    "checks_required": skill.get("checks_required", 0),
                }
            })

        result.append({
            "pillar_id": pillar.id,
            "pillar_name": pillar.name,
            "pillar_color": pillar.color,
            "pillar_icon": pillar.icon,
            "xp": xp,
            "total_checks": stats["total_checks"],
            "completed_objectives": stats["completed_objectives"],
            "skills": unlocked_skills,
        })

    return result