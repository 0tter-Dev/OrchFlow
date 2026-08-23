"""Core bootstrap-facing domain objects."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SystemStatus:
    """High-level runtime information exposed by the bootstrap layer."""

    name: str
    version: str
    status: str
    stage: str


@dataclass(frozen=True, slots=True)
class ConfigurationSummary:
    """Safe runtime configuration details exposed by delivery adapters."""

    environment: str
    api_base_url: str
    database_url: str
    database_dialect: str
    data_dir: str
    runtime_dir: str
    log_level: str


@dataclass(frozen=True, slots=True)
class DatabaseStatus:
    """High-level database connectivity details for bootstrap checks."""

    status: str
    is_connected: bool
    database_url: str
    database_dialect: str
