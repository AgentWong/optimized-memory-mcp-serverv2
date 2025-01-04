"""Alembic migration environment configuration.

This module configures the Alembic migration environment for the MCP Server database.
It handles both online and offline migration modes, loads configuration from alembic.ini,
and sets up the SQLAlchemy connection and metadata.

Environment Variables:
    DATABASE_URL: Optional database connection URL that overrides alembic.ini settings

Dependencies:
    - SQLAlchemy for database operations
    - Alembic for migration management
    - All models from src.db.models
"""

from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from src.db.init_db import Base
from src.db.models import (  # Import specific models instead of *
    ansible,
    arguments,
    entities,
    observations,
    parameters,
    providers,
    relationships,
)

# Load alembic.ini config
config = context.config

# Set SQLAlchemy URL from environment if provided
if os.getenv("DATABASE_URL"):
    config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
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
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
