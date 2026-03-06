"""Lance ce script une seule fois pour créer les badges et niveaux."""
from app.db import SessionLocal
from app.models.badge import Badge
from app.models.level import Level

db = SessionLocal()

# Niveaux
levels = [
    Level(name="Bronze",  min_xp=0,     max_xp=499),
    Level(name="Argent",  min_xp=500,   max_xp=1999),
    Level(name="Or",      min_xp=2000,  max_xp=4999),
    Level(name="Diamant", min_xp=5000,  max_xp=11999),
    Level(name="Maître",  min_xp=12000, max_xp=999999),
]

# Badges
badges = [
    Badge(name="Premier Pas",    icon="🎯", description="Première action complétée",        condition_json="first_action"),
    Badge(name="Streak Warrior", icon="🔥", description="7 jours consécutifs de score > 0", condition_json="streak_7"),
    Badge(name="Perfect Week",   icon="⭐", description="7 jours consécutifs avec score ≥ 95%", condition_json="perfect_week"),
    Badge(name="Diamond Month",  icon="💎", description="30 jours consécutifs avec score ≥ 90%", condition_json="diamond_month"),
    Badge(name="Centurion",      icon="🏆", description="100 jours de streak",               condition_json="streak_100"),
]

for l in levels:
    db.add(l)
for b in badges:
    db.add(b)

db.commit()
db.close()
print("✅ Badges et niveaux créés.")