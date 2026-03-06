"""
Tests — habit streak individuel
Couvre : streak actuel, record historique, get_all_habits_streaks (optimisé)
"""
import pytest
from datetime import date, timedelta

from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.services.habit_service import (
    get_habit_streak,
    get_all_habits_streaks,
    check_habit,
    uncheck_habit,
)

TODAY     = date.today()
YESTERDAY = TODAY - timedelta(days=1)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def habit(db):
    h = Habit(name="Sport", pillar_id=None, type="good", points=20,
              frequency="daily", is_active=True)
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


def add_log(db, habit_id: int, day: date, checked: bool = True):
    log = HabitLog(habit_id=habit_id, date=day, checked=checked, points_earned=20)
    db.add(log)
    db.commit()
    return log


# ── get_habit_streak ──────────────────────────────────────────────────────────

class TestGetHabitStreak:

    def test_aucun_log_streak_zero(self, db, habit):
        result = get_habit_streak(db, habit.id)
        assert result["current_streak"] == 0
        assert result["best_streak"]    == 0
        assert result["last_checked"]   is None
        assert result["total_checks"]   == 0

    def test_coche_aujourd_hui_streak_1(self, db, habit):
        add_log(db, habit.id, TODAY)
        result = get_habit_streak(db, habit.id)
        assert result["current_streak"] == 1
        assert result["best_streak"]    == 1
        assert result["total_checks"]   == 1

    def test_coche_hier_et_aujourd_hui_streak_2(self, db, habit):
        add_log(db, habit.id, TODAY)
        add_log(db, habit.id, YESTERDAY)
        result = get_habit_streak(db, habit.id)
        assert result["current_streak"] == 2

    def test_trou_dans_la_serie_casse_le_streak(self, db, habit):
        """Log aujourd'hui + il y a 3 jours (pas hier) → streak = 1."""
        add_log(db, habit.id, TODAY)
        add_log(db, habit.id, TODAY - timedelta(days=3))
        result = get_habit_streak(db, habit.id)
        assert result["current_streak"] == 1

    def test_streak_hier_mais_pas_aujourd_hui(self, db, habit):
        """Dernière coche = hier → streak compte quand même (fenêtre d'un jour)."""
        add_log(db, habit.id, YESTERDAY)
        add_log(db, habit.id, TODAY - timedelta(days=2))
        result = get_habit_streak(db, habit.id)
        assert result["current_streak"] == 2

    def test_streak_avant_hier_pas_hier_streak_zero(self, db, habit):
        """Dernière coche = avant-hier → streak rompu."""
        add_log(db, habit.id, TODAY - timedelta(days=2))
        result = get_habit_streak(db, habit.id)
        assert result["current_streak"] == 0

    def test_record_historique_plus_grand_que_streak_actuel(self, db, habit):
        """Ancien streak de 5, streak actuel de 2 → best_streak = 5."""
        # Ancien streak de 5 (il y a 10–14 jours)
        for i in range(10, 15):
            add_log(db, habit.id, TODAY - timedelta(days=i))
        # Streak actuel de 2
        add_log(db, habit.id, TODAY)
        add_log(db, habit.id, YESTERDAY)

        result = get_habit_streak(db, habit.id)
        assert result["current_streak"] == 2
        assert result["best_streak"]    == 5

    def test_record_egal_au_streak_actuel(self, db, habit):
        """Streak continu de 7 jours → current == best == 7."""
        for i in range(7):
            add_log(db, habit.id, TODAY - timedelta(days=i))
        result = get_habit_streak(db, habit.id)
        assert result["current_streak"] == 7
        assert result["best_streak"]    == 7

    def test_total_checks_compte_tous_les_jours(self, db, habit):
        add_log(db, habit.id, TODAY)
        add_log(db, habit.id, TODAY - timedelta(days=5))
        add_log(db, habit.id, TODAY - timedelta(days=10))
        result = get_habit_streak(db, habit.id)
        assert result["total_checks"] == 3

    def test_log_unchecked_false_ne_compte_pas(self, db, habit):
        """Un log checked=False ne doit pas compter dans le streak."""
        add_log(db, habit.id, TODAY,      checked=False)
        add_log(db, habit.id, YESTERDAY,  checked=True)
        result = get_habit_streak(db, habit.id)
        # Aujourd'hui n'est pas coché → pas de continuité depuis aujourd'hui
        # Mais hier l'est → fenêtre d'1 jour acceptée
        assert result["current_streak"] == 1


# ── check_habit → streak retourné ────────────────────────────────────────────

class TestCheckHabitReturnsStreak:

    def test_check_retourne_streak(self, db, habit):
        result = check_habit(db, habit.id)
        assert "points_earned" in result
        # Le streak est calculé dans le route, pas dans le service ici —
        # on vérifie juste que check_habit ne plante pas et retourne un log
        assert result["message"] == "Habitude cochée ✓"

    def test_double_check_idempotent(self, db, habit):
        check_habit(db, habit.id)
        result = check_habit(db, habit.id)
        assert result["message"] == "Déjà cochée aujourd'hui"

    def test_uncheck_puis_recheck(self, db, habit):
        check_habit(db, habit.id)
        uncheck_habit(db, habit.id)
        result = check_habit(db, habit.id)
        assert result["message"] == "Habitude cochée ✓"


# ── get_all_habits_streaks ────────────────────────────────────────────────────

class TestGetAllHabitsStreaks:

    def test_liste_vide_si_pas_habitudes(self, db):
        result = get_all_habits_streaks(db)
        assert result == []

    def test_retourne_une_entree_par_habitude(self, db):
        for name in ["Sport", "Lecture", "Méditation"]:
            db.add(Habit(name=name, type="good", points=10, frequency="daily", is_active=True))
        db.commit()
        result = get_all_habits_streaks(db)
        assert len(result) == 3

    def test_habitude_archivee_exclue(self, db):
        db.add(Habit(name="Actif",   type="good", points=10, frequency="daily", is_active=True))
        db.add(Habit(name="Archivé", type="good", points=10, frequency="daily", is_active=False))
        db.commit()
        result = get_all_habits_streaks(db)
        assert len(result) == 1
        assert result[0]["habit_name"] == "Actif"

    def test_streak_correct_dans_bulk(self, db):
        h1 = Habit(name="H1", type="good", points=10, frequency="daily", is_active=True)
        h2 = Habit(name="H2", type="good", points=10, frequency="daily", is_active=True)
        db.add_all([h1, h2])
        db.commit()

        # H1 : coché aujourd'hui + hier → streak 2
        add_log(db, h1.id, TODAY)
        add_log(db, h1.id, YESTERDAY)
        # H2 : aucun log → streak 0

        result = get_all_habits_streaks(db)
        by_id  = {r["habit_id"]: r for r in result}

        assert by_id[h1.id]["current_streak"] == 2
        assert by_id[h2.id]["current_streak"] == 0

    def test_structure_retournee(self, db):
        db.add(Habit(name="Test", type="good", points=10, frequency="daily", is_active=True))
        db.commit()
        result = get_all_habits_streaks(db)
        keys = result[0].keys()
        for expected in ["habit_id", "habit_name", "habit_type", "current_streak", "best_streak", "total_checks"]:
            assert expected in keys