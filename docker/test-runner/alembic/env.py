# docker/test-runner/alembic/env.py  (solo se usa en el runner de tests)
import os
import sys
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, text
from alembic import context

# Asegurar que el repo root esté en sys.path para imports de `app.*`
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.infra.persistence.base import Base #app\infra\persistence\base.py

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def _get_url():
    # Prioridad a env var del runner (.env.test)
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    # Si no, lo que diga el INI (alembic_test.ini)
    return config.get_main_option("sqlalchemy.url")

def run_migrations_offline():
    url = _get_url()
    schema = "athome" if url.startswith("postgresql") else None
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=schema,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    cfg = config.get_section(config.config_ini_section) or {}
    cfg["sqlalchemy.url"] = _get_url()
    connectable = engine_from_config(cfg, prefix="sqlalchemy.", poolclass=pool.NullPool)

    with connectable.connect() as connection:
        schema = None
        if connection.dialect.name == "postgresql":
            connection.execute(text('CREATE SCHEMA IF NOT EXISTS "athome";'))
            schema = "athome"

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            version_table_schema=schema,
        )
        with context.begin_transaction():
            context.run_migrations()
