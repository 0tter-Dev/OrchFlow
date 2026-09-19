"""Safe, shared configuration readiness diagnosis."""

from __future__ import annotations

from dataclasses import dataclass

from orchflow.infrastructure.config.settings import AppSettings


@dataclass(frozen=True, slots=True)
class ConfigurationHealthGroup:
    concern: str
    status: str
    keys: tuple[str, ...]
    remediation: str
    source: str


@dataclass(frozen=True, slots=True)
class ConfigurationHealth:
    status: str
    groups: tuple[ConfigurationHealthGroup, ...]


class ConfigurationHealthService:
    """Diagnose configured values without contacting remote services or exposing secrets."""

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    def diagnose(self) -> ConfigurationHealth:
        groups = (
            ConfigurationHealthGroup(
                "runtime_paths",
                "ready",
                ("ORCHFLOW_DATA_DIR", "ORCHFLOW_RUNTIME_DIR"),
                "Runtime paths are ready.",
                "backend settings",
            ),
            ConfigurationHealthGroup(
                "database",
                "ready",
                ("ORCHFLOW_DATABASE_URL",),
                "Run the Windows setup check if database migration is required.",
                "backend settings",
            ),
            ConfigurationHealthGroup(
                "endpoints",
                "ready",
                (
                    "ORCHFLOW_API_HOST",
                    "ORCHFLOW_API_PORT",
                    "ORCHFLOW_WEB_HOST",
                    "ORCHFLOW_WEB_PORT",
                    "ORCHFLOW_WEB_URL",
                ),
                "Use the Windows setup/check launcher to verify local API and web processes.",
                "backend and launchers",
            ),
            ConfigurationHealthGroup(
                "authentication",
                "warning" if self._settings.jwt_secret == "change-this-in-local-env" else "ready",
                (
                    "ORCHFLOW_JWT_SECRET",
                    "ORCHFLOW_JWT_ALGORITHM",
                    "ORCHFLOW_JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
                ),
                "Set a local ORCHFLOW_JWT_SECRET before sharing access beyond local development.",
                "backend settings",
            ),
            ConfigurationHealthGroup(
                "ai",
                "disabled" if not self._settings.ai_enabled else "ready",
                ("ORCHFLOW_AI_ENABLED", "ORCHFLOW_LITELLM_MODE", "ORCHFLOW_LITELLM_API_KEY"),
                "AI assistance is intentionally disabled."
                if not self._settings.ai_enabled
                else "Use AI health checks to verify the configured gateway.",
                "backend settings",
            ),
        )
        return ConfigurationHealth(
            "warning" if any(g.status == "warning" for g in groups) else "ready", groups
        )
