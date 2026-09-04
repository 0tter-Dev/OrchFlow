"""Integration coverage for configuration and persistence bootstrap."""

from __future__ import annotations

import os
from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text

from orchflow.infrastructure.config.settings import AppSettings, get_settings
from orchflow.infrastructure.persistence.base import Base
from orchflow.infrastructure.persistence.session import (
    check_database_connection,
    create_engine_from_settings,
)


def test_settings_normalize_local_paths(tmp_path: Path) -> None:
    settings = AppSettings(
        data_dir=tmp_path / "data",
        runtime_dir=tmp_path / "runtime",
        database_url="sqlite:///./data/test-settings.db",
    )

    settings.ensure_runtime_directories()

    assert settings.resolved_data_dir.exists()
    assert settings.resolved_runtime_dir.exists()
    assert settings.database_file_path is not None
    assert settings.database_file_path.parent.exists()
    assert settings.normalized_database_url.startswith("sqlite:///")


def test_ai_assistance_settings_default_to_disabled() -> None:
    settings = AppSettings()

    assert settings.ai_enabled is False
    assert settings.litellm_mode == "sdk"
    assert settings.litellm_base_url == "http://localhost:4000"
    assert settings.litellm_default_model == "ollama/llama2"
    assert settings.litellm_timeout_seconds == 60


def test_database_connection_check_succeeds_for_local_sqlite(tmp_path: Path) -> None:
    settings = AppSettings(
        data_dir=tmp_path / "data",
        runtime_dir=tmp_path / "runtime",
        database_url=f"sqlite:///{(tmp_path / 'data' / 'connectivity.db').as_posix()}",
    )

    settings.ensure_runtime_directories()

    assert check_database_connection(settings) is True


def test_alembic_upgrade_head_runs_against_local_sqlite(tmp_path: Path) -> None:
    database_path = tmp_path / "data" / "alembic.db"
    os.environ["ORCHFLOW_DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"
    os.environ["ORCHFLOW_DATA_DIR"] = str(tmp_path / "data")
    os.environ["ORCHFLOW_RUNTIME_DIR"] = str(tmp_path / "runtime")
    get_settings.cache_clear()

    try:
        config = Config("alembic.ini")
        command.upgrade(config, "head")
    finally:
        get_settings.cache_clear()
        os.environ.pop("ORCHFLOW_DATABASE_URL", None)
        os.environ.pop("ORCHFLOW_DATA_DIR", None)
        os.environ.pop("ORCHFLOW_RUNTIME_DIR", None)

    assert database_path.exists()
    migrated_settings = AppSettings(
        data_dir=tmp_path / "data",
        runtime_dir=tmp_path / "runtime",
        database_url=f"sqlite:///{database_path.as_posix()}",
    )
    engine = create_engine_from_settings(migrated_settings)
    try:
        with engine.connect() as connection:
            table_count = connection.execute(
                text(
                    "SELECT COUNT(*) FROM sqlite_master "
                    "WHERE type = 'table' AND name IN ("
                    "'users', 'user_preferences', 'audit_events', "
                    "'lifecycle_function_decisions', "
                    "'ai_authorized_context_manifests', 'ai_analysis_proposals', "
                    "'ai_analysis_proposal_reviews', "
                    "'ai_analysis_proposal_applications'"
                    ")"
                )
            ).scalar_one()
    finally:
        engine.dispose()
    assert table_count == 8


def test_alembic_revision_graph_has_single_base_and_head() -> None:
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    assert script.get_bases() == ["6bdc38282503"]
    assert script.get_heads() == ["b7c4e1d2a9f0"]


def test_alembic_head_schema_matches_sqlalchemy_metadata(tmp_path: Path) -> None:
    database_path = tmp_path / "data" / "alembic-metadata.db"
    os.environ["ORCHFLOW_DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"
    os.environ["ORCHFLOW_DATA_DIR"] = str(tmp_path / "data")
    os.environ["ORCHFLOW_RUNTIME_DIR"] = str(tmp_path / "runtime")
    get_settings.cache_clear()

    try:
        config = Config("alembic.ini")
        command.upgrade(config, "head")
    finally:
        get_settings.cache_clear()
        os.environ.pop("ORCHFLOW_DATABASE_URL", None)
        os.environ.pop("ORCHFLOW_DATA_DIR", None)
        os.environ.pop("ORCHFLOW_RUNTIME_DIR", None)

    migrated_settings = AppSettings(
        data_dir=tmp_path / "data",
        runtime_dir=tmp_path / "runtime",
        database_url=f"sqlite:///{database_path.as_posix()}",
    )
    engine = create_engine_from_settings(migrated_settings)
    try:
        with engine.connect() as connection:
            migration_context = MigrationContext.configure(connection)
            metadata_diffs = compare_metadata(migration_context, Base.metadata)
            table_names = set(inspect(connection).get_table_names())
    finally:
        engine.dispose()

    assert metadata_diffs == []
    assert set(Base.metadata.tables) <= table_names
