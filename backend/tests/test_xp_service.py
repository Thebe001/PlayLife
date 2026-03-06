"""
Tests — xp_service.py
Couvre : add_xp, get_total_xp, get_current_level
"""
import pytest
from datetime import date, timedelta

from app.models.xp_log import XPLog
from app.services.xp_service import add_xp, get_total_xp, get_current_level


TODAY = date.today()


class TestAddXp:

    def test_ajoute_xp_log(self, db):
        """add_xp crée bien un XPLog en base."""
        log = add_xp(db, xp=100, source="test")
        assert log.id is not None
        assert log.xp_delta == 100
        assert log.source == "test"

    def test_xp_persiste_en_db(self, db):
        add_xp(db, xp=50, source="scoring")
        assert db.query(XPLog).count() == 1
        assert db.query(XPLog).first().xp_delta == 50

    def test_plusieurs_add_xp(self, db):
        add_xp(db, xp=10, source="a")
        add_xp(db, xp=20, source="b")
        add_xp(db, xp=30, source="c")
        assert db.query(XPLog).count() == 3


class TestGetTotalXp:

    def test_zero_sans_logs(self, db):
        assert get_total_xp(db) == 0

    def test_somme_correcte(self, db):
        db.add_all([
            XPLog(xp_delta=100, source="a"),
            XPLog(xp_delta=200, source="b"),
            XPLog(xp_delta=300, source="c"),
        ])
        db.commit()
        assert get_total_xp(db) == 600

    def test_xp_negatif_deduit(self, db):
        """Les XP négatifs (sanctions) sont bien déduits."""
        db.add_all([
            XPLog(xp_delta=500, source="scoring"),
            XPLog(xp_delta=-100, source="sanction"),
        ])
        db.commit()
        assert get_total_xp(db) == 400

    def test_retourne_int(self, db):
        db.add(XPLog(xp_delta=42, source="test"))
        db.commit()
        result = get_total_xp(db)
        assert isinstance(result, int)


class TestGetCurrentLevel:

    def test_niveau_none_sans_levels(self, db):
        """Sans niveaux configurés → retourne None."""
        db.add(XPLog(xp_delta=500, source="test"))
        db.commit()
        assert get_current_level(db) is None

    def test_niveau_bronze_debut(self, db, levels):
        """0 XP → niveau Bronze (min_xp=0)."""
        level = get_current_level(db)
        assert level is not None
        assert level.name == "Bronze"

    def test_niveau_argent(self, db, levels):
        """1000 XP → niveau Argent."""
        db.add(XPLog(xp_delta=1000, source="test"))
        db.commit()
        assert get_current_level(db).name == "Argent"

    def test_niveau_or(self, db, levels):
        """2500 XP → niveau Or."""
        db.add(XPLog(xp_delta=2500, source="test"))
        db.commit()
        assert get_current_level(db).name == "Or"

    def test_niveau_diamant(self, db, levels):
        """5000 XP → niveau Diamant."""
        db.add(XPLog(xp_delta=5000, source="test"))
        db.commit()
        assert get_current_level(db).name == "Diamant"

    def test_niveau_master(self, db, levels):
        """10000 XP → niveau Master."""
        db.add(XPLog(xp_delta=10000, source="test"))
        db.commit()
        assert get_current_level(db).name == "Master"

    def test_niveau_frontiere_exacte(self, db, levels):
        """999 XP → encore Bronze, pas Argent."""
        db.add(XPLog(xp_delta=999, source="test"))
        db.commit()
        assert get_current_level(db).name == "Bronze"

    def test_niveau_apres_perte_xp(self, db, levels):
        """Retour en arrière si XP perdu (sanction)."""
        db.add_all([
            XPLog(xp_delta=1500, source="scoring"),
            XPLog(xp_delta=-600, source="sanction"),  # → 900 XP = Bronze
        ])
        db.commit()
        assert get_current_level(db).name == "Bronze"