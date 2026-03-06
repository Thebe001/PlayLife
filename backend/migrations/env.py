from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# Ajouter le dossier backend au path pour importer les modèles
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db import Base
from app.config import settings

# Importer tous les modèles pour qu'Alembic les détecte
from app.models import (
    pillar, habit, habit_log, objective, task,
    daily_score, global_score, xp_log, level,
    badge, badge_unlock, journal_entry, review,
    day_template, template_item,
)
from app.models import reward, reward_log, sanction, sanction_log

# Alembic config
config = context.config

# Surcharger l'URL depuis notre config centralisée
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata cible pour l'autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,   # requis pour SQLite (ALTER TABLE)
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,   # requis pour SQLite (ALTER TABLE)
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()