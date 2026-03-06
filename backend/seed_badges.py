"""Lance ce script pour créer/mettre à jour les badges et niveaux (idempotent)."""
from app.db import SessionLocal
from app.models.badge import Badge
from app.models.level import Level

db = SessionLocal()

try:
    # Niveaux — insère seulement s'ils n'existent pas déjà
    levels_data = [
        {"name": "Bronze",  "min_xp": 0,     "max_xp": 499},
        {"name": "Argent",  "min_xp": 500,   "max_xp": 1999},
        {"name": "Or",      "min_xp": 2000,  "max_xp": 4999},
        {"name": "Diamant", "min_xp": 5000,  "max_xp": 11999},
        {"name": "Maître",  "min_xp": 12000, "max_xp": 999999},
    ]
    for ld in levels_data:
        if not db.query(Level).filter(Level.name == ld["name"]).first():
            db.add(Level(**ld))

    # Badges — insère seulement s'ils n'existent pas déjà
    badges_data = [
        {"name": "Premier Pas",    "icon": "🎯", "description": "Première action complétée",        "condition_json": "first_action"},
        {"name": "Streak Warrior", "icon": "🔥", "description": "7 jours consécutifs de score > 0", "condition_json": "streak_7"},
        {"name": "Perfect Week",   "icon": "⭐", "description": "7 jours consécutifs avec score ≥ 95%", "condition_json": "perfect_week"},
        {"name": "Diamond Month",  "icon": "💎", "description": "30 jours consécutifs avec score ≥ 90%", "condition_json": "diamond_month"},
        {"name": "Centurion",      "icon": "🏆", "description": "100 jours de streak",               "condition_json": "streak_100"},
    ]
    for bd in badges_data:
        if not db.query(Badge).filter(Badge.name == bd["name"]).first():
            db.add(Badge(**bd))

    db.commit()
    print("✅ Badges et niveaux créés / vérifiés.")
finally:
    db.close()