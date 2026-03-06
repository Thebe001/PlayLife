"""
sanction_service.py
===================
Logique de déclenchement automatique des sanctions.

Règle métier (cahier des charges) :
- Une sanction a un trigger_threshold (ex: 40%) et consecutive_days (ex: 3).
- Elle se déclenche si le score global est resté SOUS le seuil pendant
  au moins `consecutive_days` jours consécutifs.
- Une sanction ne se déclenche qu'UNE SEULE FOIS par séquence :
  si elle a déjà été loguée hier pour la même séquence, on ne re-trigger pas.
- Appelé automatiquement après chaque recalcul de score global.
"""

from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.models.sanction import Sanction
from app.models.sanction_log import SanctionLog
from app.models.global_score import GlobalScore


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_recent_scores(db: Session, days: int) -> list[GlobalScore]:
    """
    Retourne les `days` derniers GlobalScore triés par date DESC.
    Une seule requête — utilisée par toutes les vérifications.
    """
    return (
        db.query(GlobalScore)
        .order_by(GlobalScore.date.desc())
        .limit(days)
        .all()
    )


def _was_triggered_today(db: Session, sanction_id: int) -> bool:
    """Vérifie si la sanction a déjà été déclenchée aujourd'hui → idempotence."""
    today = date.today()
    return (
        db.query(SanctionLog)
        .filter(
            SanctionLog.sanction_id == sanction_id,
            SanctionLog.triggered_at >= today.isoformat(),
        )
        .first()
    ) is not None


def _consecutive_days_below_threshold(
    scores: list[GlobalScore],
    threshold: float,
    required_days: int,
) -> bool:
    """
    Vérifie que les `required_days` derniers scores sont tous < threshold
    ET que les dates sont bien consécutives (pas de trous).

    Retourne True si la condition est remplie.
    """
    if len(scores) < required_days:
        return False

    # On prend les `required_days` scores les plus récents (déjà triés DESC)
    recent = scores[:required_days]

    # 1. Tous sous le seuil ?
    if not all(s.score_global < threshold for s in recent):
        return False

    # 2. Dates consécutives ? (tri DESC → recent[0] est le plus récent)
    for i in range(len(recent) - 1):
        expected_prev = recent[i].date - timedelta(days=1)
        if recent[i + 1].date != expected_prev:
            return False

    return True


# ── Service public ────────────────────────────────────────────────────────────

def check_and_trigger_sanctions(db: Session) -> list[dict]:
    """
    Point d'entrée principal — appelé après chaque calculate_global_score().

    Charge toutes les sanctions actives, vérifie chacune, déclenche si besoin.
    Optimisé : une seule requête pour les scores, une seule pour les sanctions.

    Retourne la liste des sanctions déclenchées (peut être vide).
    """
    sanctions = db.query(Sanction).all()
    if not sanctions:
        return []

    # Nombre max de jours consécutifs requis parmi toutes les sanctions
    max_days = max(s.consecutive_days for s in sanctions)
    # +1 pour avoir un peu de marge sur les vérifications de dates
    scores = _get_recent_scores(db, max_days + 1)

    if not scores:
        return []

    triggered = []

    for sanction in sanctions:
        # Idempotence : ne pas re-déclencher deux fois dans la même journée
        if _was_triggered_today(db, sanction.id):
            continue

        should_trigger = _consecutive_days_below_threshold(
            scores,
            threshold=sanction.trigger_threshold,
            required_days=sanction.consecutive_days,
        )

        if should_trigger:
            log = SanctionLog(
                sanction_id=sanction.id,
                reason=(
                    f"Score global sous {sanction.trigger_threshold}% "
                    f"pendant {sanction.consecutive_days} jour(s) consécutif(s)"
                ),
            )
            db.add(log)
            triggered.append({
                "sanction_id":   sanction.id,
                "sanction_name": sanction.name,
                "threshold":     sanction.trigger_threshold,
                "days":          sanction.consecutive_days,
                "reason":        log.reason,
            })

    if triggered:
        db.commit()

    return triggered


def get_sanction_logs(db: Session, limit: int = 50) -> list[dict]:
    """
    Retourne les derniers logs de sanctions avec le détail de la sanction.
    Un seul JOIN — pas de N+1.
    """
    rows = (
        db.query(SanctionLog, Sanction)
        .join(Sanction, SanctionLog.sanction_id == Sanction.id)
        .order_by(SanctionLog.triggered_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "log_id":        log.id,
            "sanction_id":   sanction.id,
            "sanction_name": sanction.name,
            "threshold":     sanction.trigger_threshold,
            "consecutive_days": sanction.consecutive_days,
            "triggered_at":  log.triggered_at.isoformat(),
            "reason":        log.reason,
        }
        for log, sanction in rows
    ]


def create_sanction(db: Session, name: str, description: str,
                    trigger_threshold: float, consecutive_days: int) -> Sanction:
    """Crée une nouvelle sanction."""
    sanction = Sanction(
        name=name,
        description=description,
        trigger_threshold=trigger_threshold,
        consecutive_days=consecutive_days,
    )
    db.add(sanction)
    db.commit()
    db.refresh(sanction)
    return sanction


def get_sanctions(db: Session) -> list[Sanction]:
    return db.query(Sanction).order_by(Sanction.id).all()


def delete_sanction(db: Session, sanction_id: int) -> bool:
    sanction = db.query(Sanction).filter(Sanction.id == sanction_id).first()
    if not sanction:
        return False
    db.delete(sanction)
    db.commit()
    return True