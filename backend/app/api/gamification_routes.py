from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.xp_log import XPLog
from app.services.badge_service import check_badges, get_unlocked_badges, get_global_streak
from app.services.xp_service import get_total_xp, get_current_level
from app.models.reward import Reward
from app.models.global_score import GlobalScore

router = APIRouter(prefix="/gamification", tags=["Gamification"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    """Résumé complet : XP, niveau, streak, badges, récompenses."""
    total_xp = get_total_xp(db)
    level    = get_current_level(db)
    streak   = get_global_streak(db)
    badges   = get_unlocked_badges(db)
    rewards  = db.query(Reward).filter(Reward.is_active == True).all()

    recent_scores = (
        db.query(GlobalScore)
        .order_by(GlobalScore.date.desc())
        .limit(30)
        .all()
    )

    return {
        "total_xp": total_xp,
        "level": {
            "name":    level.name    if level else "Bronze",
            "min_xp":  level.min_xp  if level else 0,
            "max_xp":  level.max_xp  if level else 499,
        },
        "streak":  streak,
        "badges":  badges,
        "rewards": [
            {
                "id":             r.id,
                "name":           r.name,
                "level_required": r.level_required,
                "reward_type":    r.reward_type,
                "cooldown_days":  r.cooldown_days,
            }
            for r in rewards
        ],
        "recent_scores": [
            {"date": str(s.date), "score": s.score_global}
            for s in recent_scores
        ],
    }


@router.post("/badges/check")
def trigger_badge_check(db: Session = Depends(get_db)):
    """Vérifie et débloque les badges mérités."""
    unlocked = check_badges(db)
    return {"unlocked": unlocked, "count": len(unlocked)}


@router.get("/badges")
def list_badges(db: Session = Depends(get_db)):
    """Liste tous les badges débloqués."""
    return get_unlocked_badges(db)


# SÉCURITÉ : route XP supprimée du client
# Les XP sont uniquement accordés par le backend (habit check, score journalier)
# Plus de route POST /xp/{amount} accessible depuis le front