"""
Fixtures partagées pour tous les tests LifeForge OS.
Utilise une DB SQLite en mémoire — isolée, sans toucher à lifeforge.db.
"""
import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models.pillar import Pillar
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.models.daily_score import DailyScore
from app.models.global_score import GlobalScore
from app.models.xp_log import XPLog
from app.models.level import Level
from app.models.badge import Badge
from app.models.badge_unlock import BadgeUnlock


# ── DB en mémoire ─────────────────────────────────────────────────────────────
@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


# ── Données de base ────────────────────────────────────────────────────────────
@pytest.fixture
def pillar_health(db):
    p = Pillar(name="Santé", weight_pct=50.0, is_active=True, color="#00ff00", icon="💪")
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@pytest.fixture
def pillar_career(db):
    p = Pillar(name="Carrière", weight_pct=50.0, is_active=True, color="#0000ff", icon="💼")
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@pytest.fixture
def habit_sport(db, pillar_health):
    h = Habit(name="Sport", pillar_id=pillar_health.id, type="good", points=10, frequency="daily", is_active=True)
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


@pytest.fixture
def levels(db):
    lvls = [
        Level(name="Bronze",   min_xp=0,    max_xp=999),
        Level(name="Argent",   min_xp=1000, max_xp=2499),
        Level(name="Or",       min_xp=2500, max_xp=4999),
        Level(name="Diamant",  min_xp=5000, max_xp=9999),
        Level(name="Master",   min_xp=10000, max_xp=999999),
    ]
    db.add_all(lvls)
    db.commit()
    return lvls