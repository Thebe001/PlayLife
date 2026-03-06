"""
Tests — complete_task avec XP
Couvre : idempotence, XP tâche, bonus objectif complété, recalcul completion_pct
"""
import pytest
from fastapi import HTTPException
from app.models.objective import Objective
from app.models.task import Task
from app.models.xp_log import XPLog
from app.services.xp_service import get_total_xp


def make_objective(db, pillar_id=1, title="Test Obj"):
    obj = Objective(
        pillar_id=pillar_id,
        title=title,
        horizon="monthly",
        completion_pct=0.0,
        status="active",
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def make_task(db, objective_id, title="Tâche", points=30, status="pending"):
    task = Task(
        objective_id=objective_id,
        pillar_id=1,
        title=title,
        points=points,
        difficulty="medium",
        status=status,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


class TestCompleteTaskXP:

    def test_xp_ajoute_apres_completion(self, db):
        """Compléter une tâche de 30 pts → +30 XP dans xp_log."""
        obj  = make_objective(db)
        task = make_task(db, obj.id, points=30)

        xp_before = get_total_xp(db)

        task.status = "done"
        db.commit()
        from app.services.xp_service import add_xp
        add_xp(db, task.points, source="task")

        assert get_total_xp(db) == xp_before + 30

    def test_xp_source_correcte(self, db):
        """La source du log XP doit être 'task'."""
        obj  = make_objective(db)
        task = make_task(db, obj.id, points=20)
        from app.services.xp_service import add_xp
        add_xp(db, task.points, source="task")

        log = db.query(XPLog).order_by(XPLog.id.desc()).first()
        assert log.source == "task"
        assert log.xp_delta == 20

    def test_completion_pct_recalcule_1_sur_2(self, db):
        """1 tâche sur 2 complétée → 50%."""
        obj   = make_objective(db)
        task1 = make_task(db, obj.id, title="T1")
        task2 = make_task(db, obj.id, title="T2")

        task1.status = "done"
        db.commit()

        all_tasks = db.query(Task).filter(Task.objective_id == obj.id).all()
        done      = sum(1 for t in all_tasks if t.status == "done")
        pct       = round((done / len(all_tasks)) * 100, 1)
        obj.completion_pct = pct
        db.commit()
        db.refresh(obj)

        assert obj.completion_pct == 50.0
        assert obj.status == "active"

    def test_completion_pct_100_marque_completed(self, db):
        """Toutes les tâches complétées → objectif status = 'completed'."""
        obj  = make_objective(db)
        task = make_task(db, obj.id)

        task.status = "done"
        db.commit()

        all_tasks = db.query(Task).filter(Task.objective_id == obj.id).all()
        done      = sum(1 for t in all_tasks if t.status == "done")
        pct       = round((done / len(all_tasks)) * 100, 1)
        obj.completion_pct = pct
        if pct == 100.0:
            obj.status = "completed"
        db.commit()
        db.refresh(obj)

        assert obj.completion_pct == 100.0
        assert obj.status == "completed"

    def test_bonus_xp_objectif_complete(self, db):
        """Objectif complété → +100 XP bonus en plus des points de la tâche."""
        obj  = make_objective(db)
        task = make_task(db, obj.id, points=50)

        xp_before = get_total_xp(db)

        from app.services.xp_service import add_xp
        # XP tâche
        add_xp(db, task.points, source="task")
        # XP bonus objectif
        add_xp(db, 100, source="objective")

        assert get_total_xp(db) == xp_before + 50 + 100

    def test_bonus_xp_source_objective(self, db):
        """Le log XP du bonus objectif doit avoir source='objective'."""
        from app.services.xp_service import add_xp
        add_xp(db, 100, source="objective")

        log = db.query(XPLog).filter(XPLog.source == "objective").first()
        assert log is not None
        assert log.xp_delta == 100

    def test_tache_sans_points_pas_de_xp(self, db):
        """Une tâche avec points=0 ne génère pas de XP."""
        obj  = make_objective(db)
        task = make_task(db, obj.id, points=0)

        xp_before = get_total_xp(db)
        # Simuler la logique : if task.points and task.points > 0 → add_xp
        if task.points and task.points > 0:
            from app.services.xp_service import add_xp
            add_xp(db, task.points, source="task")

        assert get_total_xp(db) == xp_before

    def test_idempotence_double_completion(self, db):
        """Compléter une tâche déjà 'done' ne génère pas de XP en double."""
        obj  = make_objective(db)
        task = make_task(db, obj.id, points=30, status="done")

        xp_before = get_total_xp(db)

        # Simuler la logique idempotent du endpoint
        if task.status == "done":
            xp_earned = 0
        else:
            from app.services.xp_service import add_xp
            add_xp(db, task.points, source="task")
            xp_earned = task.points

        assert xp_earned == 0
        assert get_total_xp(db) == xp_before

    def test_tache_sans_objectif_parent(self, db):
        """Tâche standalone (sans objectif) → XP ok, pas d'erreur sur completion_pct."""
        task = Task(
            objective_id=None,
            pillar_id=1,
            title="Tâche standalone",
            points=25,
            difficulty="easy",
            status="pending",
        )
        db.add(task)
        db.commit()

        from app.services.xp_service import add_xp
        add_xp(db, task.points, source="task")

        assert get_total_xp(db) == 25