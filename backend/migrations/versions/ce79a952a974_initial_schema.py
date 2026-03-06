"""initial_schema

Revision ID: ce79a952a974
Revises: 
Create Date: 2026-03-06 21:36:51.475922

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'ce79a952a974'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Indexes sur objectives (nouveaux) ──────────────
    with op.batch_alter_table('objectives', schema=None) as batch_op:
        batch_op.alter_column('pillar_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.create_index('ix_objectives_horizon', ['horizon'], unique=False)
        batch_op.create_index('ix_objectives_pillar',  ['pillar_id'], unique=False)
        batch_op.create_index('ix_objectives_status',  ['status'], unique=False)

    # ── Contraintes unique habit_logs ──────────────────
    with op.batch_alter_table('habit_logs', schema=None) as batch_op:
        batch_op.alter_column('habit_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('date',
               existing_type=sa.DATE(),
               nullable=False)
        try:
            batch_op.drop_index('uq_habitlog_habit_date')
        except Exception:
            pass
        batch_op.create_unique_constraint('uq_habitlog_habit_date', ['habit_id', 'date'])

    # ── Contraintes unique daily_scores ───────────────
    with op.batch_alter_table('daily_scores', schema=None) as batch_op:
        try:
            batch_op.drop_index('uq_dailyscore_date_pillar')
        except Exception:
            pass
        batch_op.create_unique_constraint('uq_dailyscore_date_pillar', ['date', 'pillar_id'])

    # ── NOT NULL levels ────────────────────────────────
    with op.batch_alter_table('levels', schema=None) as batch_op:
        batch_op.alter_column('name',  existing_type=sa.VARCHAR(),  nullable=False)
        batch_op.alter_column('min_xp', existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column('max_xp', existing_type=sa.INTEGER(), nullable=False)

    # ── reviews : fix llm_generated type ──────────────
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.alter_column('type',
               existing_type=sa.VARCHAR(), nullable=False)
        batch_op.alter_column('period_start',
               existing_type=sa.DATE(),    nullable=False)
        batch_op.alter_column('period_end',
               existing_type=sa.DATE(),    nullable=False)
        batch_op.alter_column('content',
               existing_type=sa.VARCHAR(), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.alter_column('content',      existing_type=sa.VARCHAR(), nullable=True)
        batch_op.alter_column('period_end',   existing_type=sa.DATE(),    nullable=True)
        batch_op.alter_column('period_start', existing_type=sa.DATE(),    nullable=True)
        batch_op.alter_column('type',         existing_type=sa.VARCHAR(), nullable=True)

    with op.batch_alter_table('levels', schema=None) as batch_op:
        batch_op.alter_column('max_xp', existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column('min_xp', existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column('name',   existing_type=sa.VARCHAR(), nullable=True)

    with op.batch_alter_table('daily_scores', schema=None) as batch_op:
        batch_op.drop_constraint('uq_dailyscore_date_pillar', type_='unique')

    with op.batch_alter_table('habit_logs', schema=None) as batch_op:
        batch_op.drop_constraint('uq_habitlog_habit_date', type_='unique')
        batch_op.alter_column('date',     existing_type=sa.DATE(),    nullable=True)
        batch_op.alter_column('habit_id', existing_type=sa.INTEGER(), nullable=True)

    with op.batch_alter_table('objectives', schema=None) as batch_op:
        batch_op.drop_index('ix_objectives_status')
        batch_op.drop_index('ix_objectives_pillar')
        batch_op.drop_index('ix_objectives_horizon')
        batch_op.alter_column('pillar_id', existing_type=sa.INTEGER(), nullable=True)