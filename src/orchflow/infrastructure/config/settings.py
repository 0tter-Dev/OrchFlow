"""Runtime settings management for OrchFlow."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

SQLITE_URL_PREFIXES = ("sqlite:///", "sqlite+pysqlite:///")
PROJECT_ROOT = Path(__file__).resolve().parents[4]


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

    env: str = "development"
    api_host: str = "localhost"
    api_port: int = 8000
    database_url: str = "sqlite:///./data/orchflow.db"
    jwt_secret: str = "change-this-in-local-env"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    ai_enabled: bool = False
    litellm_mode: str = "sdk"
    litellm_base_url: str = "http://localhost:4000"
    litellm_api_key: str = ""
    litellm_default_model: str = "ollama/llama2"
    litellm_timeout_seconds: int = 60
    local_ai_provider_url: str = "http://localhost:11434"
    runtime_dir: Path = Path("./runtime")
    data_dir: Path = Path("./data")
    log_level: str = "INFO"

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
