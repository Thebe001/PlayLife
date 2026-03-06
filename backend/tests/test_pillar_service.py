"""
Tests — pillar_service.py
Couvre : create_pillar validation poids, update_pillar, get_weight_summary
"""
import pytest
from fastapi import HTTPException
from app.models.pillar import Pillar
from app.services.pillar_service import (
    create_pillar, update_pillar, get_weight_summary, validate_weight_budget
)
from app.schemas.pillar_schema import PillarCreate


def make_pillar_data(name="Test", weight=30.0):
    return PillarCreate(name=name, icon="⭐", color="#3b82f6", weight_pct=weight)


class TestValidateWeightBudget:

    def test_premier_pilier_valide(self, db):
        """50% sur DB vide → OK."""
        validate_weight_budget(db, 50.0)  # ne lève pas

    def test_depassement_leve_422(self, db):
        """Ajouter 101% → HTTP 422."""
        with pytest.raises(HTTPException) as exc:
            validate_weight_budget(db, 101.0)
        assert exc.value.status_code == 422

    def test_exactement_100_valide(self, db):
        """100% exact → OK."""
        validate_weight_budget(db, 100.0)  # ne lève pas

    def test_depassement_avec_piliers_existants(self, db):
        """60% existant + 50% → dépasse 100% → 422."""
        db.add(Pillar(name="A", weight_pct=60.0, is_active=True))
        db.commit()
        with pytest.raises(HTTPException) as exc:
            validate_weight_budget(db, 50.0)
        assert exc.value.status_code == 422
        assert "budget restant" in exc.value.detail.lower()

    def test_exactement_complementaire(self, db):
        """60% existant + 40% → exactement 100% → OK."""
        db.add(Pillar(name="A", weight_pct=60.0, is_active=True))
        db.commit()
        validate_weight_budget(db, 40.0)  # ne lève pas

    def test_pilier_archive_exclu_du_calcul(self, db):
        """Pilier archivé ne compte pas dans le budget."""
        db.add(Pillar(name="Archivé", weight_pct=80.0, is_active=False))
        db.commit()
        validate_weight_budget(db, 100.0)  # ne lève pas car archivé ignoré

    def test_exclude_id_pour_update(self, db):
        """update_pillar : exclure le pilier lui-même évite le faux dépassement."""
        p = Pillar(name="A", weight_pct=60.0, is_active=True)
        db.add(p)
        db.commit()
        # Modifier de 60% à 70% — sans exclude_id ce serait 60+70=130%
        validate_weight_budget(db, 70.0, exclude_id=p.id)  # ne lève pas


class TestCreatePillar:

    def test_creation_simple(self, db):
        p = create_pillar(db, make_pillar_data("Santé", 50.0))
        assert p.id is not None
        assert p.name == "Santé"
        assert p.weight_pct == 50.0

    def test_creation_bloquee_si_depassement(self, db):
        db.add(Pillar(name="Existant", weight_pct=80.0, is_active=True))
        db.commit()
        with pytest.raises(HTTPException) as exc:
            create_pillar(db, make_pillar_data("Nouveau", 30.0))
        assert exc.value.status_code == 422


class TestGetWeightSummary:

    def test_vide(self, db):
        summary = get_weight_summary(db)
        assert summary["total_weight"] == 0.0
        assert summary["remaining"] == 100.0
        assert summary["is_valid"] is False

    def test_exactement_100(self, db):
        db.add(Pillar(name="A", weight_pct=60.0, is_active=True))
        db.add(Pillar(name="B", weight_pct=40.0, is_active=True))
        db.commit()
        summary = get_weight_summary(db)
        assert summary["total_weight"] == 100.0
        assert summary["remaining"] == 0.0
        assert summary["is_valid"] is True

    def test_pilier_archive_exclu(self, db):
        db.add(Pillar(name="Actif",    weight_pct=60.0, is_active=True))
        db.add(Pillar(name="Archivé",  weight_pct=40.0, is_active=False))
        db.commit()
        summary = get_weight_summary(db)
        assert summary["total_weight"] == 60.0
        assert summary["is_valid"] is False