"""
Alembic environment configuration
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.infra.persistence.base import Base
from app.infra.persistence import (
    usuarios,
    perfiles,
    servicios,
    ubicacion,
    agenda,
    matriculas,
    publicaciones,
    relaciones,
    paciente,
    valoraciones,
    auth,
)

config = context.config

env_database_url = os.getenv("DATABASE_URL")
if env_database_url:
    # Escape '%' to avoid .ini interpolation issues
    escaped_url = env_database_url.replace("%", "%%")
    config.set_main_option("sqlalchemy.url", escaped_url)

# Logging config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_object=lambda obj, name, type_, reflected, compare_to: (
            obj.schema == "athome" if hasattr(obj, "schema") else True
        ),
        version_table_schema=(
            target_metadata.schema if target_metadata.schema else None
        ),
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=lambda obj, name, type_, reflected, compare_to: (
                obj.schema == "athome" if hasattr(obj, "schema") else True
            ),
            version_table_schema=(
                target_metadata.schema if target_metadata.schema else None
            ),
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

