from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine, Base

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
    template_item
)

from app.api import (
    pillar_routes,
    habit_routes,
    scoring_routes,
    gamification_routes,
    journal_routes,
    review_routes,
    template_routes
)

app = FastAPI(title="PlayUrLife API")

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


@app.get("/")
def root():
    return {"message": "PlayUrLife backend running"}