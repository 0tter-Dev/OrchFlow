"""Shared pytest fixtures for OrchFlow tests."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

from orchflow.infrastructure.config.settings import get_settings


@pytest.fixture
def isolated_environment(tmp_path: Path) -> Iterator[None]:
    """Provide an isolated filesystem-backed environment for a test."""
    data_dir = tmp_path / "data"
    runtime_dir = tmp_path / "runtime"
    database_path = data_dir / "orchflow.db"

    previous_values = {
        "ORCHFLOW_DATABASE_URL": os.environ.get("ORCHFLOW_DATABASE_URL"),
        "ORCHFLOW_DATA_DIR": os.environ.get("ORCHFLOW_DATA_DIR"),
        "ORCHFLOW_RUNTIME_DIR": os.environ.get("ORCHFLOW_RUNTIME_DIR"),
    }

    os.environ["ORCHFLOW_DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"
    os.environ["ORCHFLOW_DATA_DIR"] = str(data_dir)
    os.environ["ORCHFLOW_RUNTIME_DIR"] = str(runtime_dir)
    get_settings.cache_clear()

    try:
        yield
    finally:
        for key, value in previous_values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        get_settings.cache_clear()
