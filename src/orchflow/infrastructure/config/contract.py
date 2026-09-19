"""The versioned, operator-safe inventory of OrchFlow configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ConfigurationClassification = Literal["required", "optional", "derived", "deprecated"]
ConfigurationOwner = Literal["backend", "launcher", "web"]


@dataclass(frozen=True, slots=True)
class ConfigurationVariable:
    """One supported configuration variable and its public contract."""

    name: str
    owner: ConfigurationOwner
    classification: ConfigurationClassification
    default: str | None
    value_format: str
    consumer: str
    sensitive: bool = False

    def redact(self, value: str | None) -> str | None:
        """Return a diagnostic-safe representation without exposing secrets."""
        if value is None or not self.sensitive:
            return value
        return "[redacted]" if value else "[not configured]"


CONFIGURATION_CONTRACT: tuple[ConfigurationVariable, ...] = (
    ConfigurationVariable(
        "ORCHFLOW_ENV", "backend", "optional", "development", "string", "settings"
    ),
    ConfigurationVariable(
        "ORCHFLOW_API_HOST", "backend", "optional", "localhost", "hostname", "settings"
    ),
    ConfigurationVariable(
        "ORCHFLOW_API_PORT", "backend", "optional", "8000", "integer (1-65535)", "settings"
    ),
    ConfigurationVariable(
        "ORCHFLOW_DATABASE_URL",
        "backend",
        "optional",
        "sqlite:///./data/orchflow.db",
        "SQLAlchemy URL",
        "settings and persistence",
    ),
    ConfigurationVariable(
        "ORCHFLOW_JWT_SECRET",
        "backend",
        "required",
        "change-this-in-local-env",
        "non-empty secret",
        "authentication",
        sensitive=True,
    ),
    ConfigurationVariable(
        "ORCHFLOW_JWT_ALGORITHM", "backend", "optional", "HS256", "JWT algorithm", "authentication"
    ),
    ConfigurationVariable(
        "ORCHFLOW_JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
        "backend",
        "optional",
        "60",
        "positive integer minutes",
        "authentication",
    ),
    ConfigurationVariable(
        "ORCHFLOW_AI_ENABLED", "backend", "optional", "false", "boolean", "AI adapter"
    ),
    ConfigurationVariable(
        "ORCHFLOW_LITELLM_MODE", "backend", "optional", "sdk", "string", "LiteLLM gateway"
    ),
    ConfigurationVariable(
        "ORCHFLOW_LITELLM_BASE_URL",
        "backend",
        "optional",
        "http://localhost:4000",
        "HTTP URL",
        "LiteLLM gateway",
    ),
    ConfigurationVariable(
        "ORCHFLOW_LITELLM_API_KEY",
        "backend",
        "optional",
        "",
        "secret",
        "LiteLLM gateway",
        sensitive=True,
    ),
    ConfigurationVariable(
        "ORCHFLOW_LITELLM_DEFAULT_MODEL",
        "backend",
        "optional",
        "ollama/llama2",
        "provider/model",
        "AI adapter",
    ),
    ConfigurationVariable(
        "ORCHFLOW_LITELLM_TIMEOUT_SECONDS",
        "backend",
        "optional",
        "60",
        "positive integer seconds",
        "LiteLLM gateway",
    ),
    ConfigurationVariable(
        "ORCHFLOW_LOCAL_AI_PROVIDER_URL",
        "backend",
        "optional",
        "http://localhost:11434",
        "HTTP URL",
        "AI adapter",
    ),
    ConfigurationVariable(
        "ORCHFLOW_RUNTIME_DIR",
        "backend",
        "optional",
        "./runtime",
        "local path",
        "settings and launchers",
    ),
    ConfigurationVariable(
        "ORCHFLOW_DATA_DIR", "backend", "optional", "./data", "local path", "settings"
    ),
    ConfigurationVariable(
        "ORCHFLOW_LOG_LEVEL", "backend", "optional", "INFO", "logging level", "settings"
    ),
    ConfigurationVariable(
        "ORCHFLOW_WEB_HOST", "launcher", "optional", "localhost", "hostname", "Windows launchers"
    ),
    ConfigurationVariable(
        "ORCHFLOW_WEB_PORT",
        "launcher",
        "optional",
        "5174",
        "integer (1-65535)",
        "Windows launchers",
    ),
    ConfigurationVariable(
        "ORCHFLOW_WEB_URL",
        "launcher",
        "derived",
        "http://localhost:5174",
        "HTTP URL",
        "Windows launchers",
    ),
    ConfigurationVariable(
        "VITE_API_BASE_URL", "web", "optional", "/orchflow-api", "URL path or URL", "web API client"
    ),
)


def configuration_variable(name: str) -> ConfigurationVariable:
    """Return a supported variable by name, failing loudly for contract drift."""
    return next(variable for variable in CONFIGURATION_CONTRACT if variable.name == name)


def redact_configuration_value(name: str, value: str | None) -> str | None:
    """Redact a configured value according to the public inventory."""
    return configuration_variable(name).redact(value)
