"""
Tests — badge_service.py
Couvre : check_badges, get_global_streak, get_unlocked_badges
"""
import pytest
from datetime import date, timedelta

from app.models.badge import Badge
from app.models.badge_unlock import BadgeUnlock
from app.models.habit_log import HabitLog
from app.models.global_score import GlobalScore
from app.models.habit import Habit
from app.models.pillar import Pillar
from app.services.badge_service import check_badges, get_global_streak, get_unlocked_badges


TODAY = date.today()


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_badge(db, name, condition):
    b = Badge(name=name, condition_json=condition, icon="🏅", description=name)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b

def make_scores(db, n_days, score_value, start_date=None):
    """Crée n_days GlobalScores consécutifs à partir d'aujourd'hui vers le passé."""
    start = start_date or TODAY
    for i in range(n_days):
        db.add(GlobalScore(date=start - timedelta(days=i), score_global=score_value, xp_earned=int(score_value)))
    db.commit()


# ─────────────────────────────────────────────────────────────────────────────
# get_global_streak
# ─────────────────────────────────────────────────────────────────────────────

class TestGetGlobalStreak:

    def test_streak_zero_sans_scores(self, db):
        assert get_global_streak(db) == 0

    def test_streak_un_jour(self, db):
        db.add(GlobalScore(date=TODAY, score_global=50.0, xp_earned=50))
        db.commit()
        assert get_global_streak(db) == 1

    def test_streak_trois_jours_consecutifs(self, db):
        make_scores(db, 3, 70.0)
        assert get_global_streak(db) == 3

    def test_streak_casse_par_score_zero(self, db):
        """Un jour à 0 interrompt le streak."""
        db.add(GlobalScore(date=TODAY,                   score_global=80.0, xp_earned=80))
        db.add(GlobalScore(date=TODAY - timedelta(days=1), score_global=0.0,  xp_earned=0))
        db.add(GlobalScore(date=TODAY - timedelta(days=2), score_global=80.0, xp_earned=80))
        db.commit()
        assert get_global_streak(db) == 1

    def test_streak_casse_par_jour_manquant(self, db):
        """Un jour manquant interrompt le streak."""
        db.add(GlobalScore(date=TODAY,                   score_global=80.0, xp_earned=80))
        # pas de score hier
        db.add(GlobalScore(date=TODAY - timedelta(days=2), score_global=80.0, xp_earned=80))
        db.commit()
        assert get_global_streak(db) == 1

    def test_streak_sept_jours(self, db):
        make_scores(db, 7, 85.0)
        assert get_global_streak(db) == 7


# ─────────────────────────────────────────────────────────────────────────────
# check_badges
# ─────────────────────────────────────────────────────────────────────────────

class TestCheckBadges:

    def test_aucun_badge_sans_conditions(self, db):
        """Pas de badges configurés → liste vide."""
        assert check_badges(db) == []

    def test_badge_first_action(self, db):
        """first_action débloqué dès le premier habit check."""
        badge = make_badge(db, "Premier Pas", "first_action")
        p = Pillar(name="Test", weight_pct=100, is_active=True)
        db.add(p)
        db.commit()
        h = Habit(name="Sport", pillar_id=p.id, type="good", points=10, frequency="daily", is_active=True)
        db.add(h)
        db.commit()
        db.add(HabitLog(habit_id=h.id, date=TODAY, checked=True, points_earned=10))
        db.commit()

        unlocked = check_badges(db)
        assert "Premier Pas" in unlocked

    def test_badge_first_action_pas_debloque_sans_check(self, db):
        """first_action ne se débloque pas sans habit log."""
        make_badge(db, "Premier Pas", "first_action")
        assert check_badges(db) == []

    def test_badge_streak_7(self, db):
        """streak_7 débloqué après 7 jours consécutifs."""
        badge = make_badge(db, "Semaine Parfaite", "streak_7")
        make_scores(db, 7, 80.0)
        unlocked = check_badges(db)
        assert "Semaine Parfaite" in unlocked

    def test_badge_streak_7_pas_debloque_avec_6_jours(self, db):
        """6 jours ne suffisent pas pour streak_7."""
        make_badge(db, "Semaine Parfaite", "streak_7")
        make_scores(db, 6, 80.0)
        assert check_badges(db) == []

    def test_badge_perfect_week(self, db):
        """perfect_week : 7 jours avec score >= 95."""
        make_badge(db, "Semaine Parfaite", "perfect_week")
        make_scores(db, 7, 95.0)
        unlocked = check_badges(db)
        assert "Semaine Parfaite" in unlocked

    def test_badge_perfect_week_echec_score_insuffisant(self, db):
        """perfect_week ne se débloque pas si un score < 95."""
        make_badge(db, "Semaine Parfaite", "perfect_week")
        make_scores(db, 6, 95.0)
        db.add(GlobalScore(date=TODAY - timedelta(days=6), score_global=94.9, xp_earned=94))
        db.commit()
        assert check_badges(db) == []

    def test_badge_deja_debloque_non_redonne(self, db):
        """Un badge déjà unlocked ne réapparaît pas."""
        badge = make_badge(db, "Premier Pas", "first_action")
        db.add(BadgeUnlock(badge_id=badge.id, unlocked_at=TODAY))
        p = Pillar(name="Test", weight_pct=100, is_active=True)
        db.add(p)
        db.commit()
        h = Habit(name="Sport", pillar_id=p.id, type="good", points=10, frequency="daily", is_active=True)
        db.add(h)
        db.commit()
        db.add(HabitLog(habit_id=h.id, date=TODAY, checked=True, points_earned=10))
        db.commit()

        assert check_badges(db) == []

    def test_plusieurs_badges_debloques_ensemble(self, db):
        """Plusieurs badges peuvent être débloqués en un seul appel."""
        make_badge(db, "Premier Pas", "first_action")
        make_badge(db, "Semaine", "streak_7")
        p = Pillar(name="Test", weight_pct=100, is_active=True)
        db.add(p)
        db.commit()
        h = Habit(name="Sport", pillar_id=p.id, type="good", points=10, frequency="daily", is_active=True)
        db.add(h)
        db.commit()
        db.add(HabitLog(habit_id=h.id, date=TODAY, checked=True, points_earned=10))
        db.commit()
        make_scores(db, 7, 80.0)

        unlocked = check_badges(db)
        assert "Premier Pas" in unlocked
        assert "Semaine" in unlocked


# ─────────────────────────────────────────────────────────────────────────────
# get_unlocked_badges
# ─────────────────────────────────────────────────────────────────────────────

class TestGetUnlockedBadges:

    def test_liste_vide_sans_unlocks(self, db):
        assert get_unlocked_badges(db) == []

    def test_retourne_badge_debloque(self, db):
        badge = make_badge(db, "Premier Pas", "first_action")
        db.add(BadgeUnlock(badge_id=badge.id, unlocked_at=TODAY))
        db.commit()

        result = get_unlocked_badges(db)
        assert len(result) == 1
        assert result[0]["name"] == "Premier Pas"
        assert result[0]["icon"] == "🏅"

    def test_structure_retournee(self, db):
        """Vérifie que tous les champs attendus sont présents."""
        badge = make_badge(db, "Test", "first_action")
        db.add(BadgeUnlock(badge_id=badge.id, unlocked_at=TODAY))
        db.commit()

        result = get_unlocked_badges(db)
        keys = result[0].keys()
        assert "id" in keys
        assert "name" in keys
        assert "icon" in keys
        assert "description" in keys
        assert "unlocked_at" in keys

    def test_pas_de_doublons(self, db):
        """Même si on appelle plusieurs fois, pas de doublons."""
        badge = make_badge(db, "Unique", "first_action")
        db.add(BadgeUnlock(badge_id=badge.id, unlocked_at=TODAY))
        db.commit()

        r1 = get_unlocked_badges(db)
        r2 = get_unlocked_badges(db)
        assert len(r1) == len(r2) == 1

    def test_ordre_plus_recent_en_premier(self, db):
        """Les badges les plus récents apparaissent en premier."""
        b1 = make_badge(db, "Ancien", "streak_7")
        b2 = make_badge(db, "Recent", "first_action")
        db.add(BadgeUnlock(badge_id=b1.id, unlocked_at=TODAY - timedelta(days=5)))
        db.add(BadgeUnlock(badge_id=b2.id, unlocked_at=TODAY))
        db.commit()

        result = get_unlocked_badges(db)
        assert result[0]["name"] == "Recent"
        assert result[1]["name"] == "Ancien"