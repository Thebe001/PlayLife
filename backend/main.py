from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.db import engine, Base

# Import all models so SQLAlchemy creates the tables
from app.models import (
    pillar, habit, habit_log, objective, task,
    daily_score, global_score, xp_log, level,
    badge, badge_unlock, journal_entry, review,
    day_template, template_item,
)
from app.models import reward, reward_log, sanction, sanction_log

from app.api import (
    pillar_routes, habit_routes, scoring_routes,
    gamification_routes, journal_routes, review_routes,
    template_routes, stats_routes, voice_routes, backup_routes,
)
from app.api import objective_routes, reward_routes, skilltree_routes

# ── Rate limiter (localhost only → limites généreuses) ──────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["300/minute"],   # 300 req/min globalement
)

app = FastAPI(
    title="LifeForge OS API",
    version=settings.APP_VERSION,
    description="Your Personal Life Operating System — Backend API",
)

# Attacher le limiter à l'app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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
app.include_router(skilltree_routes.router)


@app.get("/")
def root():
    return {
        "message": "LifeForge OS backend running ✓",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
def health():
    """Endpoint de santé — utile pour vérifier que le backend tourne."""
    return {"status": "ok"}