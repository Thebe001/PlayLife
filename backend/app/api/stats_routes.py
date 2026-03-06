"""
stats_routes.py — mis à jour Feature C
Ajoute l'endpoint /stats/correlation pour la corrélation mood vs score.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from typing import Optional

from app.db import get_db
from app.models.journal_entry import JournalEntry
from app.models.global_score import GlobalScore
from app.models.habit_log import HabitLog
from app.models.habit import Habit
from app.models.xp_log import XPLog

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/correlation")
def mood_score_correlation(
    days: int = 30,
    db: Session = Depends(get_db),
):
    """
    Corrélation humeur (mood) vs score global.

    Pour chaque jour où il y a à la fois un journal ET un score :
    - Retourne les paires (date, mood, energy, score)
    - Calcule la corrélation moyenne par niveau de mood
    - Identifie les patterns : "quand mood >= 4, score moyen = X%"

    Paramètres :
        days : fenêtre temporelle (défaut 30 jours)
    """
    end_date   = date.today()
    start_date = end_date - timedelta(days=days)

    # Charger les journaux avec mood
    journals = (
        db.query(JournalEntry)
        .filter(
            JournalEntry.date >= start_date,
            JournalEntry.date <= end_date,
            JournalEntry.mood.isnot(None),
        )
        .all()
    )

    # Charger les scores globaux
    scores = (
        db.query(GlobalScore)
        .filter(
            GlobalScore.date >= start_date,
            GlobalScore.date <= end_date,
        )
        .all()
    )

    # Indexer par date
    score_by_date = {s.date: s.score_global for s in scores}

    # Construire les paires
    pairs = []
    for journal in journals:
        score = score_by_date.get(journal.date)
        if score is not None:
            pairs.append({
                "date":   journal.date.isoformat(),
                "mood":   journal.mood,
                "energy": journal.energy,
                "score":  round(score, 1),
            })

    if not pairs:
        return {
            "pairs":             [],
            "by_mood":           {},
            "by_energy":         {},
            "insight":           None,
            "data_points":       0,
            "period_days":       days,
        }

    # ── Agrégation par niveau de mood (1–5) ──────────────────────────────
    mood_groups: dict[int, list[float]] = {}
    for p in pairs:
        m = p["mood"]
        if m not in mood_groups:
            mood_groups[m] = []
        mood_groups[m].append(p["score"])

    by_mood = {
        m: {
            "avg_score":  round(sum(scores) / len(scores), 1),
            "count":      len(scores),
            "min_score":  round(min(scores), 1),
            "max_score":  round(max(scores), 1),
        }
        for m, scores in sorted(mood_groups.items())
    }

    # ── Agrégation par niveau d'énergie ──────────────────────────────────
    energy_groups: dict[int, list[float]] = {}
    for p in pairs:
        if p["energy"] is not None:
            e = p["energy"]
            if e not in energy_groups:
                energy_groups[e] = []
            energy_groups[e].append(p["score"])

    by_energy = {
        e: {
            "avg_score": round(sum(scores) / len(scores), 1),
            "count":     len(scores),
        }
        for e, scores in sorted(energy_groups.items())
    }

    # ── Insight automatique ───────────────────────────────────────────────
    insight = _generate_insight(by_mood, by_energy)

    return {
        "pairs":       pairs,
        "by_mood":     by_mood,
        "by_energy":   by_energy,
        "insight":     insight,
        "data_points": len(pairs),
        "period_days": days,
    }


def _generate_insight(
    by_mood:   dict,
    by_energy: dict,
) -> str | None:
    """Génère un insight textuel simple basé sur les corrélations."""
    if not by_mood:
        return None

    # Trouver le mood avec le meilleur score moyen
    best_mood = max(by_mood.items(), key=lambda x: x[1]["avg_score"])
    worst_mood = min(by_mood.items(), key=lambda x: x[1]["avg_score"])

    delta = best_mood[1]["avg_score"] - worst_mood[1]["avg_score"]

    if delta < 5:
        return "Ton humeur n'a pas d'impact mesurable sur ton score. Continue comme ça !"

    mood_labels = {1: "😞 très bas", 2: "😕 bas", 3: "😐 neutre", 4: "😊 bon", 5: "😄 excellent"}

    best_label  = mood_labels.get(best_mood[0],  str(best_mood[0]))
    worst_label = mood_labels.get(worst_mood[0], str(worst_mood[0]))

    return (
        f"Quand ton humeur est {best_label}, ton score moyen est {best_mood[1]['avg_score']}% "
        f"(vs {worst_mood[1]['avg_score']}% quand tu te sens {worst_label}). "
        f"Différence : +{round(delta, 1)} points."
    )


@router.get("/heatmap")
def score_heatmap(
    days: int = 90,
    db: Session = Depends(get_db),
):
    """
    Données de heatmap : score global par jour sur les N derniers jours.
    Format compatible GitHub contribution graph.
    """
    end_date   = date.today()
    start_date = end_date - timedelta(days=days)

    scores = (
        db.query(GlobalScore)
        .filter(GlobalScore.date >= start_date)
        .order_by(GlobalScore.date.asc())
        .all()
    )

    return [
        {
            "date":  s.date.isoformat(),
            "score": round(s.score_global, 1),
            "level": (
                4 if s.score_global >= 98 else
                3 if s.score_global >= 90 else
                2 if s.score_global >= 75 else
                1 if s.score_global >= 60 else
                0
            ),
        }
        for s in scores
    ]


@router.get("/progression")
def score_progression(
    days: int = 30,
    db: Session = Depends(get_db),
):
    """Score global + XP par jour sur N jours — pour les courbes de progression."""
    end_date   = date.today()
    start_date = end_date - timedelta(days=days)

    scores = (
        db.query(GlobalScore)
        .filter(GlobalScore.date >= start_date)
        .order_by(GlobalScore.date.asc())
        .all()
    )

    return [
        {
            "date":   s.date.isoformat(),
            "score":  round(s.score_global, 1),
            "xp":     s.xp_earned,
        }
        for s in scores
    ]