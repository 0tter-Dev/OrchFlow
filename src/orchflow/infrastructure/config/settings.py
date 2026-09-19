"""Runtime settings management for OrchFlow."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from orchflow.infrastructure.config.contract import CONFIGURATION_CONTRACT

SQLITE_URL_PREFIXES = ("sqlite:///", "sqlite+pysqlite:///")
PROJECT_ROOT = Path(__file__).resolve().parents[4]


def _contract_default(name: str) -> str:
    default = next(variable.default for variable in CONFIGURATION_CONTRACT if variable.name == name)
    assert default is not None
    return default


def _resolve_project_path(value: Path) -> Path:
    if value.is_absolute():
        return value
    return (PROJECT_ROOT / value).resolve()


def _normalize_sqlite_url(database_url: str) -> str:
    for prefix in SQLITE_URL_PREFIXES:
        if database_url.startswith(prefix):
            raw_path = database_url.removeprefix(prefix)
            if raw_path == ":memory:":
                return database_url
            resolved_path = _resolve_project_path(Path(raw_path))
            return f"{prefix}{resolved_path.as_posix()}"
    return database_url


class AppSettings(BaseSettings):
    """Validated runtime settings loaded from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ORCHFLOW_",
        case_sensitive=False,
        extra="ignore",
    )

    env: str = _contract_default("ORCHFLOW_ENV")
    api_host: str = _contract_default("ORCHFLOW_API_HOST")
    api_port: int = Field(
        default=int(_contract_default("ORCHFLOW_API_PORT")),
        ge=1,
        le=65535,
    )
    database_url: str = _contract_default("ORCHFLOW_DATABASE_URL")
    jwt_secret: str = _contract_default("ORCHFLOW_JWT_SECRET")
    jwt_algorithm: str = _contract_default("ORCHFLOW_JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=int(_contract_default("ORCHFLOW_JWT_ACCESS_TOKEN_EXPIRE_MINUTES")),
        gt=0,
    )
    ai_enabled: bool = _contract_default("ORCHFLOW_AI_ENABLED").lower() == "true"
    litellm_mode: str = _contract_default("ORCHFLOW_LITELLM_MODE")
    litellm_base_url: str = _contract_default("ORCHFLOW_LITELLM_BASE_URL")
    litellm_api_key: str = _contract_default("ORCHFLOW_LITELLM_API_KEY")
    litellm_default_model: str = _contract_default("ORCHFLOW_LITELLM_DEFAULT_MODEL")
    litellm_timeout_seconds: int = int(_contract_default("ORCHFLOW_LITELLM_TIMEOUT_SECONDS"))
    local_ai_provider_url: str = _contract_default("ORCHFLOW_LOCAL_AI_PROVIDER_URL")
    runtime_dir: Path = Path(_contract_default("ORCHFLOW_RUNTIME_DIR"))
    data_dir: Path = Path(_contract_default("ORCHFLOW_DATA_DIR"))
    log_level: str = _contract_default("ORCHFLOW_LOG_LEVEL")

    @property
    def api_base_url(self) -> str:
        return f"http://{self.api_host}:{self.api_port}"

    @property
    def resolved_runtime_dir(self) -> Path:
        return _resolve_project_path(self.runtime_dir)

    @property
    def resolved_data_dir(self) -> Path:
        return _resolve_project_path(self.data_dir)

    @property
    def normalized_database_url(self) -> str:
        return _normalize_sqlite_url(self.database_url)

    @property
    def database_dialect(self) -> str:
        return self.normalized_database_url.split(":", 1)[0]

    @property
    def database_file_path(self) -> Path | None:
        for prefix in SQLITE_URL_PREFIXES:
            if self.normalized_database_url.startswith(prefix):
                raw_path = self.normalized_database_url.removeprefix(prefix)
                if raw_path == ":memory:":
                    return None
                return Path(raw_path)
        return None

    def ensure_runtime_directories(self) -> None:
        """Create local runtime folders required by the configured environment."""
        self.resolved_data_dir.mkdir(parents=True, exist_ok=True)
        self.resolved_runtime_dir.mkdir(parents=True, exist_ok=True)

        if self.database_file_path is not None:
            self.database_file_path.parent.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return cached application settings for the current process."""
    settings = AppSettings()
    settings.ensure_runtime_directories()
    return settings
