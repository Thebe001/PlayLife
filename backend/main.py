from fastapi import FastAPI

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

from app.api import pillar_routes
from app.api import habit_routes
from app.api import scoring_routes
from app.api import gamification_routes
from app.api import journal_routes
from app.api import review_routes
from app.api import template_routes


app = FastAPI(title="PlayUrLife API")

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