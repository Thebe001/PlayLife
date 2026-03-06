"""
Tests — focus_service.py + challenge_service.py
"""
import pytest
from datetime import date, timedelta

from app.models.habit import Habit
from app.models.pillar import Pillar
from app.models.global_score import GlobalScore
from app.models.daily_score import DailyScore
from app.models.habit_log import HabitLog
from app.models.xp_log import XPLog
from app.services.focus_service import (
    log_focus_session,
    get_focus_stats_today,
    get_focus_stats_by_pillar,
    get_focus_minutes_for_pillar,
)
from app.services.challenge_service import generate_weekly_challenge

TODAY = date.today()
WEEK_START = TODAY - timedelta(days=TODAY.weekday())


# ── focus_service ─────────────────────────────────────────────────────────────

class TestLogFocusSession:

    def test_log_session_complete(self, db):
        result = log_focus_session(db, duration_min=25, mode="pomodoro", completed=True)
        assert result["xp_earned"]   == 25
        assert result["duration_min"] == 25
        assert result["completed"]    is True

    def test_log_session_incomplete_pas_de_xp(self, db):
        result = log_focus_session(db, duration_min=10, mode="pomodoro", completed=False)
        assert result["xp_earned"] == 0

    def test_duree_trop_courte_erreur(self, db):
        result = log_focus_session(db, duration_min=0)
        assert "error" in result

    def test_xp_log_cree_en_db(self, db):
        log_focus_session(db, duration_min=25, completed=True)
        xp = db.query(XPLog).filter(XPLog.source == "focus").first()
        assert xp is not None
        assert xp.xp_delta == 25

    def test_session_incomplete_pas_de_xp_log(self, db):
        log_focus_session(db, duration_min=10, completed=False)
        xp = db.query(XPLog).filter(XPLog.source == "focus").first()
        assert xp is None

    def test_xp_proportionnel_duree(self, db):
        result = log_focus_session(db, duration_min=50, completed=True)
        assert result["xp_earned"] == 50

    def test_pilier_enregistre(self, db):
        p = Pillar(name="Santé", weight_pct=50, is_active=True)
        db.add(p)
        db.commit()
        result = log_focus_session(db, duration_min=25, pillar_id=p.id, completed=True)
        assert result["pillar_id"] == p.id

    def test_deux_sessions_xp_cumules(self, db):
        log_focus_session(db, duration_min=25, completed=True)
        log_focus_session(db, duration_min=25, completed=True)
        total = db.query(XPLog).filter(XPLog.source == "focus").count()
        assert total == 2


class TestGetFocusStatsToday:

    def test_stats_vides(self, db):
        stats = get_focus_stats_today(db)
        assert stats["total_sessions"]    == 0
        assert stats["total_minutes"]     == 0
        assert stats["completed_sessions"] == 0

    def test_une_session_complete(self, db):
        log_focus_session(db, duration_min=25, completed=True)
        stats = get_focus_stats_today(db)
        assert stats["total_sessions"]    == 1
        assert stats["completed_sessions"] == 1
        assert stats["total_minutes"]     == 25

    def test_mix_complete_incomplete(self, db):
        log_focus_session(db, duration_min=25, completed=True)
        log_focus_session(db, duration_min=10, completed=False)
        stats = get_focus_stats_today(db)
        assert stats["total_sessions"]    == 2
        assert stats["completed_sessions"] == 1
        assert stats["total_minutes"]     == 35


class TestGetFocusByPillar:

    def test_vide(self, db):
        assert get_focus_stats_by_pillar(db) == []

    def test_minutes_par_pilier(self, db):
        p = Pillar(name="Santé", weight_pct=50, is_active=True)
        db.add(p)
        db.commit()
        log_focus_session(db, duration_min=25, pillar_id=p.id, completed=True)
        log_focus_session(db, duration_min=25, pillar_id=p.id, completed=True)

        stats = get_focus_stats_by_pillar(db)
        assert len(stats) == 1
        assert stats[0]["total_minutes"] == 50

    def test_sessions_incompletes_exclues(self, db):
        p = Pillar(name="Santé", weight_pct=50, is_active=True)
        db.add(p)
        db.commit()
        log_focus_session(db, duration_min=10, pillar_id=p.id, completed=False)
        assert get_focus_stats_by_pillar(db) == []

    def test_focus_minutes_for_pillar(self, db):
        p = Pillar(name="Santé", weight_pct=50, is_active=True)
        db.add(p)
        db.commit()
        log_focus_session(db, duration_min=25, pillar_id=p.id, completed=True)
        assert get_focus_minutes_for_pillar(db, p.id) == 25

    def test_focus_minutes_autre_pilier_ignore(self, db):
        p1 = Pillar(name="Santé",   weight_pct=50, is_active=True)
        p2 = Pillar(name="Carrière", weight_pct=50, is_active=True)
        db.add_all([p1, p2])
        db.commit()
        log_focus_session(db, duration_min=25, pillar_id=p1.id, completed=True)
        assert get_focus_minutes_for_pillar(db, p2.id) == 0


# ── challenge_service ─────────────────────────────────────────────────────────

class TestGenerateWeeklyChallenge:

    def test_retourne_structure_complete(self, db):
        result = generate_weekly_challenge(db)
        assert "challenge"    in result
        assert "progress"     in result
        assert "week_start"   in result
        assert "week_end"     in result
        assert "days_elapsed" in result

    def test_challenge_a_xp_reward(self, db):
        result = generate_weekly_challenge(db)
        assert result["challenge"]["xp_reward"] > 0

    def test_challenge_score_faible(self, db):
        """Score moyen faible → défi score_target ou recovery."""
        for i in range(7):
            db.add(GlobalScore(
                date=WEEK_START - timedelta(days=7 + i),
                score_global=50.0,
                xp_earned=50,
            ))
        db.add(GlobalScore(date=TODAY, score_global=40.0, xp_earned=40))
        db.commit()

        result = generate_weekly_challenge(db)
        assert result["challenge"]["type"] in ("score", "recovery", "neglected", "pillar")

    def test_challenge_pilier_faible(self, db):
        """Pilier avec score < 50% → défi pillar ou neglected."""
        p = Pillar(name="Santé", weight_pct=100, is_active=True)
        db.add(p)
        db.commit()
        db.add(DailyScore(
            date=TODAY, pillar_id=p.id,
            score_pct=30.0, points_earned=30, points_max=100,
        ))
        db.commit()

        result = generate_weekly_challenge(db)
        assert result["challenge"]["type"] in ("pillar", "neglected", "score", "recovery")

    def test_progress_structure(self, db):
        result = generate_weekly_challenge(db)
        p = result["progress"]
        assert "current"  in p
        assert "target"   in p
        assert "pct"      in p
        assert "achieved" in p
        assert isinstance(p["achieved"], bool)

    def test_pct_dans_bornes(self, db):
        result = generate_weekly_challenge(db)
        pct = result["progress"]["pct"]
        assert 0 <= pct <= 100