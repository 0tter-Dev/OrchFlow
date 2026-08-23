"""Database engine and session management for OrchFlow."""

from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from orchflow.infrastructure.config.settings import AppSettings, get_settings
from orchflow.infrastructure.persistence import models as persistence_models
from orchflow.infrastructure.persistence.base import Base


def create_engine_from_settings(settings: AppSettings | None = None) -> Engine:
    """Create a SQLAlchemy engine from the current application settings."""
    current_settings = settings or get_settings()
    current_settings.ensure_runtime_directories()
    return create_engine(
        current_settings.normalized_database_url,
        future=True,
        pool_pre_ping=True,
    )


def create_session_factory(
    settings: AppSettings | None = None,
) -> sessionmaker[Session]:
    """Create a SQLAlchemy session factory for the configured database."""
    engine = create_engine_from_settings(settings)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def initialize_database(settings: AppSettings | None = None) -> None:
    """Initialize the configured database with the current metadata set."""
    _ = persistence_models
    engine = create_engine_from_settings(settings)
    try:
        Base.metadata.create_all(bind=engine)
    finally:
        engine.dispose()


def check_database_connection(settings: AppSettings | None = None) -> bool:
    """Return whether the configured database is reachable."""
    engine = create_engine_from_settings(settings)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    finally:
        engine.dispose()
