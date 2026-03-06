"""
Tests — scoring_service.py
Couvre : calculate_daily_scores, calculate_global_score, get_today_summary
"""
import pytest
from datetime import date, timedelta

from app.models.pillar import Pillar
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.models.daily_score import DailyScore
from app.models.global_score import GlobalScore
from app.models.xp_log import XPLog
from app.services.scoring_service import (
    calculate_daily_scores,
    calculate_global_score,
    get_today_summary,
)


TODAY = date.today()


# ─────────────────────────────────────────────────────────────────────────────
# calculate_daily_scores
# ─────────────────────────────────────────────────────────────────────────────

class TestCalculateDailyScores:

    def test_score_calcule_correctement(self, db, pillar_health, habit_sport):
        """10 pts gagnés sur 10 pts max → 100%."""
        db.add(HabitLog(habit_id=habit_sport.id, date=TODAY, checked=True, points_earned=10))
        db.commit()

        results = calculate_daily_scores(db, TODAY)

        assert len(results) == 1
        assert results[0].score_pct == 100.0
        assert results[0].points_earned == 10
        assert results[0].points_max == 10

    def test_score_partiel(self, db, pillar_health, habit_sport):
        """5 pts sur 10 → 50%."""
        db.add(HabitLog(habit_id=habit_sport.id, date=TODAY, checked=True, points_earned=5))
        db.commit()

        results = calculate_daily_scores(db, TODAY)

        assert results[0].score_pct == 50.0

    def test_score_zero_si_pas_de_logs(self, db, pillar_health):
        """Aucun log → liste vide (pas de calcul sans données)."""
        results = calculate_daily_scores(db, TODAY)
        assert results == []

    def test_score_clamp_max_100(self, db, pillar_health, habit_sport):
        """Points gagnés > points max → score plafonné à 100."""
        db.add(HabitLog(habit_id=habit_sport.id, date=TODAY, checked=True, points_earned=999))
        db.commit()

        results = calculate_daily_scores(db, TODAY)
        assert results[0].score_pct == 100.0

    def test_upsert_met_a_jour_score_existant(self, db, pillar_health, habit_sport):
        """Appeler deux fois recalcule et met à jour sans dupliquer."""
        db.add(HabitLog(habit_id=habit_sport.id, date=TODAY, checked=True, points_earned=5))
        db.commit()
        calculate_daily_scores(db, TODAY)

        # Simuler un recalcul avec plus de points
        log = db.query(HabitLog).first()
        log.points_earned = 10
        db.commit()
        results = calculate_daily_scores(db, TODAY)

        assert len(results) == 1
        assert results[0].score_pct == 100.0
        assert db.query(DailyScore).count() == 1  # pas de doublon

    def test_deux_piliers_independants(self, db, pillar_health, pillar_career):
        """Deux piliers → deux DailyScores distincts."""
        habit_h = Habit(name="Sport", pillar_id=pillar_health.id, type="good", points=10, frequency="daily", is_active=True)
        habit_c = Habit(name="Coder", pillar_id=pillar_career.id, type="good", points=20, frequency="daily", is_active=True)
        db.add_all([habit_h, habit_c])
        db.commit()

        db.add(HabitLog(habit_id=habit_h.id, date=TODAY, checked=True, points_earned=10))
        db.add(HabitLog(habit_id=habit_c.id, date=TODAY, checked=True, points_earned=20))
        db.commit()

        results = calculate_daily_scores(db, TODAY)
        assert len(results) == 2


# ─────────────────────────────────────────────────────────────────────────────
# calculate_global_score
# ─────────────────────────────────────────────────────────────────────────────

class TestCalculateGlobalScore:

    def _setup_daily_scores(self, db, pillar, score_pct):
        ds = DailyScore(
            date=TODAY,
            pillar_id=pillar.id,
            score_pct=score_pct,
            points_earned=score_pct,
            points_max=100,
        )
        db.add(ds)
        db.commit()

    def test_score_global_un_pilier(self, db, pillar_health):
        """Un seul pilier à 80% → score global 80."""
        self._setup_daily_scores(db, pillar_health, 80.0)
        result = calculate_global_score(db, TODAY)
        assert result.score_global == 80.0

    def test_score_global_deux_piliers_egaux(self, db, pillar_health, pillar_career):
        """50% health + 50% career, poids égaux → moyenne exacte."""
        self._setup_daily_scores(db, pillar_health, 60.0)
        self._setup_daily_scores(db, pillar_career, 80.0)
        result = calculate_global_score(db, TODAY)
        assert result.score_global == 70.0

    def test_score_global_sans_donnees(self, db):
        """Pas de DailyScore → score global 0."""
        result = calculate_global_score(db, TODAY)
        assert result == {"date": str(TODAY), "score_global": 0, "xp_earned": 0}

    def test_xp_earned_egal_score_global(self, db, pillar_health):
        """xp_earned = int(score_global)."""
        self._setup_daily_scores(db, pillar_health, 75.5)
        result = calculate_global_score(db, TODAY)
        assert result.xp_earned == 75

    def test_upsert_global_score(self, db, pillar_health):
        """Appeler deux fois ne crée pas de doublon."""
        self._setup_daily_scores(db, pillar_health, 80.0)
        calculate_global_score(db, TODAY)
        calculate_global_score(db, TODAY)
        assert db.query(GlobalScore).count() == 1

    def test_pilier_inactif_exclu(self, db, pillar_health, pillar_career):
        """Un pilier inactif ne compte pas dans le score global."""
        pillar_career.is_active = False
        db.commit()
        self._setup_daily_scores(db, pillar_health, 60.0)
        self._setup_daily_scores(db, pillar_career, 100.0)  # ne doit pas compter
        result = calculate_global_score(db, TODAY)
        assert result.score_global == 60.0


# ─────────────────────────────────────────────────────────────────────────────
# get_today_summary
# ─────────────────────────────────────────────────────────────────────────────

class TestGetTodaySummary:

    def test_summary_vide(self, db):
        """Sans données, renvoie des valeurs à zéro."""
        summary = get_today_summary(db)
        assert summary["global_score"] == 0
        assert summary["xp_today"] == 0
        assert summary["pillars"] == []

    def test_summary_avec_donnees(self, db, pillar_health):
        """Vérifie la structure complète du résumé."""
        ds = DailyScore(date=TODAY, pillar_id=pillar_health.id,
                        score_pct=75.0, points_earned=75, points_max=100)
        gs = GlobalScore(date=TODAY, score_global=75.0, xp_earned=75)
        xp = XPLog(date=TODAY, xp_delta=50, source="test")
        db.add_all([ds, gs, xp])
        db.commit()

        summary = get_today_summary(db)

        assert summary["global_score"] == 75.0
        assert summary["xp_today"] == 50
        assert len(summary["pillars"]) == 1
        assert summary["pillars"][0]["pillar_name"] == "Santé"
        assert summary["pillars"][0]["score_pct"] == 75.0

    def test_xp_today_somme_plusieurs_logs(self, db):
        """xp_today additionne tous les XPLog du jour."""
        db.add_all([
            XPLog(date=TODAY, xp_delta=30, source="scoring"),
            XPLog(date=TODAY, xp_delta=20, source="badge"),
            XPLog(date=TODAY - timedelta(days=1), xp_delta=100, source="hier"),  # ne doit pas compter
        ])
        db.commit()

        summary = get_today_summary(db)
        assert summary["xp_today"] == 50  # 30 + 20, pas 150