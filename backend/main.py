from fastapi import FastAPI

from app.db import engine, Base
from app.models import pillar, habit, habit_log, objective, task
from app.models import daily_score
from app.models import global_score
from app.models import xp_log
from app.models import level
from app.models import badge
from app.models import badge_unlock

from app.api import pillar_routes
from app.api import habit_routes
from app.api import scoring_routes
from app.api import gamification_routes

app = FastAPI(title="PlayUrLife API")

Base.metadata.create_all(bind=engine)

app.include_router(pillar_routes.router)
app.include_router(habit_routes.router)
app.include_router(scoring_routes.router)
app.include_router(gamification_routes.router)


@app.get("/")
def root():
    return {"message": "PlayUrLife backend running"}