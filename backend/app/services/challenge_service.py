"""
challenge_service.py
====================
Génération automatique de défis hebdomadaires personnalisés.

Les défis sont générés sans LLM — basés sur les données réelles de l'utilisateur :
- Pilier le plus faible de la semaine → défi ciblé
- Habitude jamais cochée → défi de régularité
- Streak en cours → défi de maintien
- Score global → défi de progression

Un défi a une récompense en XP et une condition de succès vérifiable.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.models.global_score import GlobalScore
from app.models.daily_score import DailyScore
from app.models.habit_log import HabitLog
from app.models.habit import Habit
from app.models.pillar import Pillar
from app.models.xp_log import XPLog


# ── Types de défis disponibles ────────────────────────────────────────────────

CHALLENGE_TEMPLATES = [
    {
        "id":          "score_target",
        "title":       "Score objectif",
        "description": "Atteins un score global de {target}% ou plus sur 3 jours cette semaine.",
        "icon":        "🎯",
        "xp_reward":   150,
        "type":        "score",
    },
    {
        "id":          "pillar_boost",
        "title":       "Renforcer {pillar}",
        "description": "Atteins 80% sur le pilier {pillar} au moins 4 jours cette semaine.",
        "icon":        "💪",
        "xp_reward":   100,
        "type":        "pillar",
    },
    {
        "id":          "habit_streak",
        "title":       "Streak sans faille",
        "description": "Coche l'habitude '{habit}' tous les jours de la semaine (7/7).",
        "icon":        "🔥",
        "xp_reward":   200,
        "type":        "habit",
    },
    {
        "id":          "consistency",
        "title":       "Semaine parfaite",
        "description": "Score global ≥ 75% chaque jour pendant 7 jours consécutifs.",
        "icon":        "⭐",
        "xp_reward":   300,
        "type":        "week",
    },
    {
        "id":          "recovery",
        "title":       "Rebond",
        "description": "Remonte ton score de {delta}% par rapport à la semaine dernière.",
        "icon":        "📈",
        "xp_reward":   120,
        "type":        "recovery",
    },
    {
        "id":          "pillar_neglected",
        "title":       "Pilier négligé",
        "description": "Coche au moins 1 habitude du pilier {pillar} chaque jour cette semaine.",
        "icon":        "🌱",
        "xp_reward":   100,
        "type":        "neglected",
    },
]


# ── Génération du défi de la semaine ─────────────────────────────────────────

def generate_weekly_challenge(db: Session) -> dict:
    """
    Génère le défi de la semaine basé sur les données réelles.

    Logique de sélection :
    1. Si score moyen < 60% → défi score_target
    2. Si pilier avec score < 50% → défi pillar_boost
    3. Si habitude jamais cochée cette semaine → défi habit_streak
    4. Si score en progression → défi consistency
    5. Sinon → défi recovery (viser mieux que la semaine d'avant)
    """
    today      = date.today()
    week_start = today - timedelta(days=today.weekday())  # Lundi de la semaine courante
    last_week_start = week_start - timedelta(days=7)

    # ── Données de la semaine courante ────────────────────────────────────
    current_scores = (
        db.query(GlobalScore)
        .filter(GlobalScore.date >= week_start)
        .all()
    )
    avg_current = (
        sum(s.score_global for s in current_scores) / len(current_scores)
        if current_scores else 0
    )

    # ── Données de la semaine dernière ────────────────────────────────────
    last_scores = (
        db.query(GlobalScore)
        .filter(
            GlobalScore.date >= last_week_start,
            GlobalScore.date < week_start,
        )
        .all()
    )
    avg_last = (
        sum(s.score_global for s in last_scores) / len(last_scores)
        if last_scores else 0
    )

    # ── Pilier le plus faible ─────────────────────────────────────────────
    weakest_pillar = _get_weakest_pillar(db, week_start)

    # ── Habitude la moins cochée ──────────────────────────────────────────
    neglected_habit = _get_neglected_habit(db, week_start)

    # ── Sélection du type de défi ─────────────────────────────────────────
    challenge = None

    if avg_current < 60 and avg_last > 0:
        # Score faible → défi de remontée
        target = min(round(avg_last + 10), 90)
        tpl    = next(t for t in CHALLENGE_TEMPLATES if t["id"] == "score_target")
        challenge = {
            **tpl,
            "title":       tpl["title"],
            "description": tpl["description"].format(target=target),
            "target":      target,
            "context":     f"Score actuel : {round(avg_current, 1)}%",
        }

    elif weakest_pillar and weakest_pillar["avg_score"] < 50:
        # Pilier négligé
        tpl = next(t for t in CHALLENGE_TEMPLATES if t["id"] == "pillar_neglected")
        challenge = {
            **tpl,
            "title":       f"Pilier négligé — {weakest_pillar['name']}",
            "description": tpl["description"].format(pillar=weakest_pillar["name"]),
            "pillar_id":   weakest_pillar["id"],
            "context":     f"Score {weakest_pillar['name']} : {round(weakest_pillar['avg_score'], 1)}%",
        }

    elif neglected_habit:
        # Habitude jamais faite cette semaine
        tpl = next(t for t in CHALLENGE_TEMPLATES if t["id"] == "habit_streak")
        challenge = {
            **tpl,
            "title":       f"7/7 — {neglected_habit['name']}",
            "description": tpl["description"].format(habit=neglected_habit["name"]),
            "habit_id":    neglected_habit["id"],
            "context":     f"'{neglected_habit['name']}' pas encore cochée cette semaine.",
        }

    elif avg_current >= 75:
        # Bon score → défi consistency
        tpl = next(t for t in CHALLENGE_TEMPLATES if t["id"] == "consistency")
        challenge = {
            **tpl,
            "context": f"Score actuel : {round(avg_current, 1)}% — tu peux faire 7/7 !",
        }

    else:
        # Par défaut : améliorer vs semaine dernière
        delta = max(round(avg_last * 0.1), 5)
        tpl   = next(t for t in CHALLENGE_TEMPLATES if t["id"] == "recovery")
        challenge = {
            **tpl,
            "description": tpl["description"].format(delta=round(delta, 1)),
            "target":      round(avg_last + delta, 1),
            "context":     f"Semaine dernière : {round(avg_last, 1)}% — vise {round(avg_last + delta, 1)}%",
        }

    # ── Calcul de la progression courante vers le défi ────────────────────
    progress = _calculate_challenge_progress(db, challenge, week_start)

    return {
        "week_start":   week_start.isoformat(),
        "week_end":     (week_start + timedelta(days=6)).isoformat(),
        "challenge":    challenge,
        "progress":     progress,
        "avg_score_this_week": round(avg_current, 1),
        "avg_score_last_week": round(avg_last, 1),
        "days_elapsed": (today - week_start).days + 1,
    }


def _get_weakest_pillar(db: Session, since: date) -> dict | None:
    """Retourne le pilier avec le score moyen le plus bas depuis `since`."""
    pillars = db.query(Pillar).filter(Pillar.is_active == True).all()
    if not pillars:
        return None

    results = []
    for pillar in pillars:
        scores = (
            db.query(DailyScore)
            .filter(DailyScore.pillar_id == pillar.id, DailyScore.date >= since)
            .all()
        )
        if scores:
            avg = sum(s.score_pct for s in scores) / len(scores)
            results.append({"id": pillar.id, "name": pillar.name, "avg_score": avg})

    if not results:
        return None
    return min(results, key=lambda x: x["avg_score"])


def _get_neglected_habit(db: Session, since: date) -> dict | None:
    """Retourne une habitude active qui n'a pas été cochée depuis `since`."""
    habits = db.query(Habit).filter(Habit.is_active == True, Habit.type == "good").all()
    if not habits:
        return None

    for habit in habits:
        checked = (
            db.query(HabitLog)
            .filter(
                HabitLog.habit_id == habit.id,
                HabitLog.date >= since,
                HabitLog.checked == True,
            )
            .first()
        )
        if not checked:
            return {"id": habit.id, "name": habit.name}

    return None


def _calculate_challenge_progress(
    db:         Session,
    challenge:  dict,
    week_start: date,
) -> dict:
    """Calcule la progression vers le défi de la semaine."""
    today        = date.today()
    days_elapsed = (today - week_start).days + 1
    days_total   = 7

    challenge_type = challenge.get("type", "")

    if challenge_type == "score":
        target = challenge.get("target", 75)
        scores = (
            db.query(GlobalScore)
            .filter(GlobalScore.date >= week_start, GlobalScore.score_global >= target)
            .count()
        )
        return {
            "current": scores,
            "target":  3,
            "unit":    "jours ≥ cible",
            "pct":     round(min(scores / 3, 1) * 100),
            "achieved": scores >= 3,
        }

    elif challenge_type in ("pillar", "neglected"):
        pillar_id = challenge.get("pillar_id")
        if not pillar_id:
            return {"current": 0, "target": 4, "unit": "jours", "pct": 0, "achieved": False}
        days_ok = (
            db.query(DailyScore)
            .filter(
                DailyScore.pillar_id == pillar_id,
                DailyScore.date >= week_start,
                DailyScore.score_pct >= (80 if challenge_type == "pillar" else 1),
            )
            .count()
        )
        target = 4 if challenge_type == "pillar" else 7
        return {
            "current":  days_ok,
            "target":   target,
            "unit":     "jours",
            "pct":      round(min(days_ok / target, 1) * 100),
            "achieved": days_ok >= target,
        }

    elif challenge_type == "habit":
        habit_id = challenge.get("habit_id")
        if not habit_id:
            return {"current": 0, "target": 7, "unit": "jours", "pct": 0, "achieved": False}
        checked_days = (
            db.query(HabitLog)
            .filter(
                HabitLog.habit_id == habit_id,
                HabitLog.date >= week_start,
                HabitLog.checked == True,
            )
            .count()
        )
        return {
            "current":  checked_days,
            "target":   7,
            "unit":     "jours",
            "pct":      round(min(checked_days / 7, 1) * 100),
            "achieved": checked_days >= 7,
        }

    elif challenge_type == "week":
        days_75 = (
            db.query(GlobalScore)
            .filter(GlobalScore.date >= week_start, GlobalScore.score_global >= 75)
            .count()
        )
        return {
            "current":  days_75,
            "target":   7,
            "unit":     "jours ≥ 75%",
            "pct":      round(min(days_75 / 7, 1) * 100),
            "achieved": days_75 >= 7,
        }

    else:
        # Recovery : score moyen
        scores = (
            db.query(GlobalScore)
            .filter(GlobalScore.date >= week_start)
            .all()
        )
        avg = sum(s.score_global for s in scores) / len(scores) if scores else 0
        target = challenge.get("target", avg + 10)
        return {
            "current":  round(avg, 1),
            "target":   round(target, 1),
            "unit":     "% moyen",
            "pct":      round(min(avg / target, 1) * 100) if target > 0 else 0,
            "achieved": avg >= target,
        }