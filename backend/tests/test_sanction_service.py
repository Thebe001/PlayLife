"""
Tests — sanction_service.py
Couvre : auto-trigger, idempotence, dates non-consécutives, seuils exacts,
         plusieurs sanctions simultanées, get_sanction_logs
"""
import pytest
from datetime import date, timedelta, datetime, timezone

from app.models.sanction import Sanction
from app.models.sanction_log import SanctionLog
from app.models.global_score import GlobalScore
from app.services.sanction_service import (
    check_and_trigger_sanctions,
    get_sanction_logs,
    create_sanction,
    get_sanctions,
    delete_sanction,
)

TODAY     = date.today()
YESTERDAY = TODAY - timedelta(days=1)
D2        = TODAY - timedelta(days=2)
D3        = TODAY - timedelta(days=3)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_sanction(db, name="Sanction Test", threshold=40.0, days=1):
    s = Sanction(name=name, trigger_threshold=threshold, consecutive_days=days)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def make_score(db, day: date, score: float):
    gs = GlobalScore(date=day, score_global=score, xp_earned=int(score))
    db.add(gs)
    db.commit()
    return gs


# ── check_and_trigger_sanctions ───────────────────────────────────────────────

class TestCheckAndTriggerSanctions:

    def test_pas_de_sanctions_configurees(self, db):
        """Aucune sanction → retourne liste vide."""
        make_score(db, TODAY, 20.0)
        result = check_and_trigger_sanctions(db)
        assert result == []

    def test_pas_de_scores(self, db):
        """Aucun score → rien ne se déclenche."""
        make_sanction(db)
        result = check_and_trigger_sanctions(db)
        assert result == []

    def test_trigger_score_sous_seuil_1_jour(self, db):
        """Score < threshold sur 1 jour → sanction déclenchée."""
        s = make_sanction(db, threshold=40.0, days=1)
        make_score(db, TODAY, 30.0)
        result = check_and_trigger_sanctions(db)
        assert len(result) == 1
        assert result[0]["sanction_id"] == s.id
        assert result[0]["sanction_name"] == "Sanction Test"

    def test_pas_trigger_score_au_dessus_seuil(self, db):
        """Score >= threshold → aucun déclenchement."""
        make_sanction(db, threshold=40.0, days=1)
        make_score(db, TODAY, 40.0)  # exactement au seuil → pas déclenché
        result = check_and_trigger_sanctions(db)
        assert result == []

    def test_pas_trigger_score_largement_au_dessus(self, db):
        make_sanction(db, threshold=40.0, days=1)
        make_score(db, TODAY, 85.0)
        result = check_and_trigger_sanctions(db)
        assert result == []

    def test_trigger_consecutif_2_jours(self, db):
        """2 jours consécutifs sous seuil → déclenchement."""
        s = make_sanction(db, threshold=50.0, days=2)
        make_score(db, TODAY,      30.0)
        make_score(db, YESTERDAY,  35.0)
        result = check_and_trigger_sanctions(db)
        assert len(result) == 1
        assert result[0]["sanction_id"] == s.id

    def test_pas_trigger_seulement_1_jour_sur_2_requis(self, db):
        """Seulement aujourd'hui sous seuil, hier OK → pas de déclenchement."""
        make_sanction(db, threshold=50.0, days=2)
        make_score(db, TODAY,      30.0)
        make_score(db, YESTERDAY,  75.0)  # au-dessus du seuil
        result = check_and_trigger_sanctions(db)
        assert result == []

    def test_pas_trigger_dates_non_consecutives(self, db):
        """Trou dans les dates → pas de déclenchement même si scores bas."""
        make_sanction(db, threshold=50.0, days=2)
        make_score(db, TODAY, 20.0)
        make_score(db, D2,    20.0)  # D2 = avant-hier, pas hier → trou
        result = check_and_trigger_sanctions(db)
        assert result == []

    def test_trigger_3_jours_consecutifs(self, db):
        """3 jours consécutifs → déclenchement."""
        s = make_sanction(db, threshold=60.0, days=3)
        make_score(db, TODAY,      40.0)
        make_score(db, YESTERDAY,  45.0)
        make_score(db, D2,         50.0)
        result = check_and_trigger_sanctions(db)
        assert len(result) == 1
        assert result[0]["days"] == 3

    def test_idempotence_double_appel(self, db):
        """Deux appels dans la même journée → une seule sanction loguée."""
        make_sanction(db, threshold=40.0, days=1)
        make_score(db, TODAY, 20.0)

        r1 = check_and_trigger_sanctions(db)
        r2 = check_and_trigger_sanctions(db)

        assert len(r1) == 1
        assert len(r2) == 0  # idempotent

        logs = db.query(SanctionLog).all()
        assert len(logs) == 1

    def test_plusieurs_sanctions_declenchees(self, db):
        """Deux sanctions dont les conditions sont remplies → deux logs."""
        make_sanction(db, name="Sanction A", threshold=50.0, days=1)
        make_sanction(db, name="Sanction B", threshold=70.0, days=1)
        make_score(db, TODAY, 30.0)  # sous les deux seuils

        result = check_and_trigger_sanctions(db)
        assert len(result) == 2
        names = {r["sanction_name"] for r in result}
        assert names == {"Sanction A", "Sanction B"}

    def test_une_seule_sanction_declenchee_sur_deux(self, db):
        """Score à 55% → sous 70% mais pas sous 40%."""
        make_sanction(db, name="Faible",  threshold=40.0, days=1)
        make_sanction(db, name="Moyen",   threshold=70.0, days=1)
        make_score(db, TODAY, 55.0)

        result = check_and_trigger_sanctions(db)
        assert len(result) == 1
        assert result[0]["sanction_name"] == "Moyen"

    def test_log_cree_en_db(self, db):
        """Vérifie que le SanctionLog est bien persisté en base."""
        s = make_sanction(db, threshold=40.0, days=1)
        make_score(db, TODAY, 10.0)

        check_and_trigger_sanctions(db)

        log = db.query(SanctionLog).filter(SanctionLog.sanction_id == s.id).first()
        assert log is not None
        assert log.sanction_id == s.id
        assert "40.0%" in log.reason or "40%" in log.reason

    def test_reason_contient_infos_utiles(self, db):
        """Le champ reason doit mentionner le seuil et les jours."""
        make_sanction(db, threshold=35.0, days=2)
        make_score(db, TODAY,     20.0)
        make_score(db, YESTERDAY, 25.0)

        result = check_and_trigger_sanctions(db)
        assert len(result) == 1
        reason = result[0]["reason"]
        assert "35.0" in reason
        assert "2" in reason


# ── get_sanction_logs ─────────────────────────────────────────────────────────

class TestGetSanctionLogs:

    def test_vide_sans_logs(self, db):
        assert get_sanction_logs(db) == []

    def test_retourne_log_avec_details(self, db):
        s = make_sanction(db, name="Test Log", threshold=40.0, days=1)
        make_score(db, TODAY, 10.0)
        check_and_trigger_sanctions(db)

        logs = get_sanction_logs(db)
        assert len(logs) == 1
        assert logs[0]["sanction_name"] == "Test Log"
        assert "triggered_at" in logs[0]

    def test_structure_retournee(self, db):
        s = make_sanction(db, threshold=40.0, days=1)
        make_score(db, TODAY, 10.0)
        check_and_trigger_sanctions(db)

        log = get_sanction_logs(db)[0]
        for key in ["log_id", "sanction_id", "sanction_name", "threshold",
                    "consecutive_days", "triggered_at", "reason"]:
            assert key in log

    def test_limite_respectee(self, db):
        """Le paramètre limit est respecté."""
        s = make_sanction(db, threshold=40.0, days=1)
        # Créer plusieurs logs manuellement
        for _ in range(5):
            db.add(SanctionLog(sanction_id=s.id, reason="test"))
        db.commit()

        logs = get_sanction_logs(db, limit=3)
        assert len(logs) == 3


# ── CRUD sanctions ────────────────────────────────────────────────────────────

class TestCRUDSanctions:

    def test_create_sanction(self, db):
        s = create_sanction(db, "No Netflix", "desc", 50.0, 3)
        assert s.id is not None
        assert s.name == "No Netflix"
        assert s.trigger_threshold == 50.0
        assert s.consecutive_days == 3

    def test_get_sanctions_vide(self, db):
        assert get_sanctions(db) == []

    def test_get_sanctions_avec_donnees(self, db):
        make_sanction(db, name="A")
        make_sanction(db, name="B")
        assert len(get_sanctions(db)) == 2

    def test_delete_sanction(self, db):
        s = make_sanction(db)
        result = delete_sanction(db, s.id)
        assert result is True
        assert get_sanctions(db) == []

    def test_delete_inexistant(self, db):
        assert delete_sanction(db, 9999) is False