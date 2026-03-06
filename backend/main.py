from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine, Base

# Import all models so SQLAlchemy creates the tables
from app.models import (
    pillar,
    habit,
    habit_log,
    objective,
    task,
    daily_score,
    global_score,
    xp_log,
    level,
    badge,
    badge_unlock,
    journal_entry,
    review,
    day_template,
    template_item,
)
from app.models import reward, reward_log, sanction, sanction_log

from app.api import (
    pillar_routes,
    habit_routes,
    scoring_routes,
    gamification_routes,
    journal_routes,
    review_routes,
    template_routes,
    stats_routes,
    voice_routes,
    backup_routes,
)
from app.api import objective_routes, reward_routes
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Précharger Whisper au démarrage pour éviter le timeout
    print("🎤 Préchargement Whisper...")
    from app.services.whisper_service import get_model
    get_model()
    print("✅ Whisper prêt.")
    yield

app = FastAPI(title="LifeForge OS API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(pillar_routes.router)
app.include_router(habit_routes.router)
app.include_router(scoring_routes.router)
app.include_router(gamification_routes.router)
app.include_router(journal_routes.router)
app.include_router(review_routes.router)
app.include_router(template_routes.router)
app.include_router(objective_routes.router)
app.include_router(reward_routes.router)
app.include_router(stats_routes.router)
app.include_router(voice_routes.router)
app.include_router(backup_routes.router)    

@app.get("/")
def root():
    return {"message": "LifeForge OS backend running ✓", "version": "0.2.0"}