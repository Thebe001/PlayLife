from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db import get_db
from app.models.reward import Reward
from app.models.reward_log import RewardLog
from app.models.sanction import Sanction
from app.models.sanction_log import SanctionLog

router = APIRouter(prefix="/rewards", tags=["Rewards & Sanctions"])


class RewardCreate(BaseModel):
    name: str
    level_required: str = "bronze"
    reward_type: str = "consumable"
    cooldown_days: int = 0


class SanctionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_threshold: float = 40.0
    consecutive_days: int = 1


# ── Rewards ────────────────────────────────────────────

@router.post("/")
def create_reward(data: RewardCreate, db: Session = Depends(get_db)):
    reward = Reward(**data.dict())
    db.add(reward)
    db.commit()
    db.refresh(reward)
    return reward


@router.get("/")
def list_rewards(db: Session = Depends(get_db)):
    return db.query(Reward).filter(Reward.is_active == True).all()


@router.post("/{reward_id}/consume")
def consume_reward(reward_id: int, db: Session = Depends(get_db)):
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not reward:
        raise HTTPException(status_code=404, detail="Récompense introuvable")

    # Vérifier cooldown
    if reward.cooldown_days > 0:
        last_use = (
            db.query(RewardLog)
            .filter(RewardLog.reward_id == reward_id)
            .order_by(RewardLog.consumed_at.desc())
            .first()
        )
        if last_use:
            delta = datetime.utcnow() - last_use.consumed_at
            if delta.days < reward.cooldown_days:
                remaining = reward.cooldown_days - delta.days
                raise HTTPException(
                    status_code=400,
                    detail=f"Cooldown actif — disponible dans {remaining} jour(s)"
                )

    log = RewardLog(reward_id=reward_id)
    db.add(log)

    # One-shot : désactiver après consommation
    if reward.reward_type == "oneshot":
        reward.is_active = False

    db.commit()
    return {"message": f"Récompense '{reward.name}' consommée 🎉"}


# ── Sanctions ──────────────────────────────────────────

@router.post("/sanctions/")
def create_sanction(data: SanctionCreate, db: Session = Depends(get_db)):
    sanction = Sanction(**data.dict())
    db.add(sanction)
    db.commit()
    db.refresh(sanction)
    return sanction


@router.get("/sanctions/")
def list_sanctions(db: Session = Depends(get_db)):
    return db.query(Sanction).all()

@router.delete("/{reward_id}")
def delete_reward(reward_id: int, db: Session = Depends(get_db)):
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not reward:
        raise HTTPException(status_code=404, detail="Introuvable")
    db.delete(reward)
    db.commit()
    return {"message": "Supprimée"}


@router.delete("/sanctions/{sanction_id}")
def delete_sanction(sanction_id: int, db: Session = Depends(get_db)):
    sanction = db.query(Sanction).filter(Sanction.id == sanction_id).first()
    if not sanction:
        raise HTTPException(status_code=404, detail="Introuvable")
    db.delete(sanction)
    db.commit()
    return {"message": "Supprimée"}

@router.get("/sanctions/active")
def get_active_sanctions(db: Session = Depends(get_db)):
    """Retourne les sanctions déclenchées aujourd'hui."""
    today = datetime.utcnow().date()
    logs = (
        db.query(SanctionLog, Sanction)
        .join(Sanction, SanctionLog.sanction_id == Sanction.id)
        .filter(SanctionLog.triggered_at >= today)
        .all()
    )
    return [
        {"sanction": s.name, "reason": sl.reason, "triggered_at": sl.triggered_at}
        for sl, s in logs
    ]