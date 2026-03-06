"""
skilltree_routes.py — mis à jour Feature A
Intègre focus_minutes comme critère de déblocage des nœuds.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models.pillar import Pillar
from app.models.habit_log import HabitLog
from app.models.habit import Habit
from app.models.objective import Objective
from app.services.focus_service import get_focus_minutes_for_pillar

router = APIRouter(prefix="/skilltree", tags=["Skill Tree"])


def get_pillar_xp(db: Session, pillar_id: int) -> int:
    """XP gagné sur un pilier = somme des points des habitudes cochées."""
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
    focus_minutes = get_focus_minutes_for_pillar(db, pillar_id)

    return {
        "total_checks":          total_checks,
        "completed_objectives":  completed_objectives,
        "focus_minutes":         focus_minutes,
    }


# ── Skill Tree définition ─────────────────────────────────────────────────────
# Chaque nœud peut avoir :
#   xp_required          : XP pilier minimum
#   checks_required      : habitudes cochées minimum
#   objectives_required  : objectifs complétés minimum
#   focus_minutes_required : minutes de focus sur ce pilier minimum
# ─────────────────────────────────────────────────────────────────────────────

SKILL_TREES = {
    "default": [
        # ── Tier 1 — Débutant ─────────────────────────────────────────────
        {
            "id":                    "starter",
            "label":                 "Premier Pas",
            "icon":                  "🌱",
            "description":           "Tu as commencé ton parcours sur ce pilier.",
            "xp_required":           0,
            "checks_required":       0,
            "objectives_required":   0,
            "focus_minutes_required": 0,
            "tier":                  1,
            "position":              {"x": 0, "y": 0},
        },
        # ── Tier 2 — Intermédiaire ────────────────────────────────────────
        {
            "id":                    "consistent",
            "label":                 "Consistance",
            "icon":                  "🔄",
            "description":           "10 habitudes cochées sur ce pilier.",
            "xp_required":           50,
            "checks_required":       10,
            "objectives_required":   0,
            "focus_minutes_required": 0,
            "tier":                  2,
            "position":              {"x": -1, "y": 1},
        },
        {
            "id":                    "focused",
            "label":                 "Focus",
            "icon":                  "🎯",
            "description":           "25 minutes de focus sur ce pilier.",
            "xp_required":           50,
            "checks_required":       0,
            "objectives_required":   0,
            "focus_minutes_required": 25,   # 1 Pomodoro complet
            "tier":                  2,
            "position":              {"x": 1, "y": 1},
        },
        # ── Tier 3 — Avancé ───────────────────────────────────────────────
        {
            "id":                    "dedicated",
            "label":                 "Dédié",
            "icon":                  "💪",
            "description":           "30 habitudes cochées sur ce pilier.",
            "xp_required":           150,
            "checks_required":       30,
            "objectives_required":   0,
            "focus_minutes_required": 0,
            "tier":                  3,
            "position":              {"x": -2, "y": 2},
        },
        {
            "id":                    "achiever",
            "label":                 "Réalisateur",
            "icon":                  "🏆",
            "description":           "1 objectif complété + 2h de focus sur ce pilier.",
            "xp_required":           200,
            "checks_required":       0,
            "objectives_required":   1,
            "focus_minutes_required": 120,  # 2h de focus
            "tier":                  3,
            "position":              {"x": 0, "y": 2},
        },
        {
            "id":                    "expert",
            "label":                 "Expert",
            "icon":                  "⭐",
            "description":           "300 XP gagnés sur ce pilier.",
            "xp_required":           300,
            "checks_required":       0,
            "objectives_required":   0,
            "focus_minutes_required": 0,
            "tier":                  3,
            "position":              {"x": 2, "y": 2},
        },
        # ── Tier 4 — Maître ───────────────────────────────────────────────
        {
            "id":                    "master",
            "label":                 "Maître",
            "icon":                  "👑",
            "description":           "100 habitudes + 3 objectifs + 5h de focus.",
            "xp_required":           500,
            "checks_required":       100,
            "objectives_required":   3,
            "focus_minutes_required": 300,  # 5h de focus
            "tier":                  4,
            "position":              {"x": -1, "y": 3},
        },
        {
            "id":                    "legend",
            "label":                 "Légende",
            "icon":                  "🌟",
            "description":           "1000 XP + 10h de focus sur ce pilier.",
            "xp_required":           1000,
            "checks_required":       0,
            "objectives_required":   0,
            "focus_minutes_required": 600,  # 10h de focus
            "tier":                  4,
            "position":              {"x": 1, "y": 3},
        },
    ]
}


@router.get("/")
def get_skill_tree(db: Session = Depends(get_db)):
    """Retourne le skill tree complet pour tous les piliers actifs."""
    pillars = db.query(Pillar).filter(Pillar.is_active == True).all()

    result = []
    for pillar in pillars:
        xp    = get_pillar_xp(db, pillar.id)
        stats = get_pillar_stats(db, pillar.id)

        unlocked_skills = []
        for skill in SKILL_TREES["default"]:
            xp_ok      = xp    >= skill["xp_required"]
            checks_ok  = stats["total_checks"]         >= skill.get("checks_required", 0)
            obj_ok     = stats["completed_objectives"]  >= skill.get("objectives_required", 0)
            focus_ok   = stats["focus_minutes"]         >= skill.get("focus_minutes_required", 0)
            unlocked   = xp_ok and checks_ok and obj_ok and focus_ok

            unlocked_skills.append({
                **skill,
                "unlocked": unlocked,
                "progress": {
                    "xp_current":            xp,
                    "xp_required":           skill["xp_required"],
                    "checks_current":        stats["total_checks"],
                    "checks_required":       skill.get("checks_required", 0),
                    "objectives_current":    stats["completed_objectives"],
                    "objectives_required":   skill.get("objectives_required", 0),
                    "focus_minutes_current": stats["focus_minutes"],
                    "focus_minutes_required": skill.get("focus_minutes_required", 0),
                },
            })

        result.append({
            "pillar_id":             pillar.id,
            "pillar_name":           pillar.name,
            "pillar_color":          pillar.color,
            "pillar_icon":           pillar.icon,
            "xp":                    xp,
            "total_checks":          stats["total_checks"],
            "completed_objectives":  stats["completed_objectives"],
            "focus_minutes":         stats["focus_minutes"],
            "skills":                unlocked_skills,
        })

    return result