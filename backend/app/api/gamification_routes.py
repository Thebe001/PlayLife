from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.xp_service import add_xp, get_total_xp, get_current_level
from app.services.badge_service import check_badges, get_global_streak, get_unlocked_badges
from app.models.reward import Reward
from app.models.reward_log import RewardLog
from app.models.global_score import GlobalScore

router = APIRouter(prefix="/gamification", tags=["Gamification"])


@router.get("/summary")
def gamification_summary(db: Session = Depends(get_db)):
    """Résumé complet pour la page Gamification."""

    total_xp = get_total_xp(db)
    level = get_current_level(db)
    streak = get_global_streak(db)
    badges = get_unlocked_badges(db)
    rewards = db.query(Reward).filter(Reward.is_active == True).all()

    # Scores récents pour l'historique
    recent_scores = (
        db.query(GlobalScore)
        .order_by(GlobalScore.date.desc())
        .limit(7)
        .all()
    )

    return {
        "total_xp": total_xp,
        "level": {
            "name": level.name if level else "Bronze",
            "min_xp": level.min_xp if level else 0,
            "max_xp": level.max_xp if level else 500,
        } if level else {"name": "Bronze", "min_xp": 0, "max_xp": 500},
        "streak": streak,
        "badges": badges,
        "rewards": [
            {
                "id": r.id,
                "name": r.name,
                "level_required": r.level_required,
                "reward_type": r.reward_type,
                "cooldown_days": r.cooldown_days,
            }
            for r in rewards
        ],
        "recent_scores": [
            {"date": str(s.date), "score": s.score_global}
            for s in reversed(recent_scores)
        ],
    }


@router.post("/xp/{amount}")
def add_xp_action(amount: int, db: Session = Depends(get_db)):
    return add_xp(db, amount, "manual")


@router.get("/xp")
def get_xp(db: Session = Depends(get_db)):
    return {"total_xp": get_total_xp(db)}


@router.get("/level")
def current_level(db: Session = Depends(get_db)):
    return get_current_level(db)


@router.get("/streak")
def current_streak(db: Session = Depends(get_db)):
    return {"streak": get_global_streak(db)}


@router.post("/badges/check")
def check_badges_action(db: Session = Depends(get_db)):
    return check_badges(db)


@router.get("/badges")
def list_badges(db: Session = Depends(get_db)):
    return get_unlocked_badges(db)