"""Bootstrap application service used by the initial API and CLI surfaces."""

from orchflow import __version__
from orchflow.domain.system_status import ConfigurationSummary, DatabaseStatus, SystemStatus
from orchflow.infrastructure.config.settings import AppSettings, get_settings
from orchflow.infrastructure.persistence.session import (
    check_database_connection,
    initialize_database,
)


class BootstrapStatusService:
    """Provides stable bootstrap metadata for non-business entrypoints."""

    def __init__(self, settings: AppSettings | None = None) -> None:
        self._settings = settings or get_settings()
        initialize_database(self._settings)

    def get_status(self) -> SystemStatus:
        """Return the current bootstrap status exposed by the app surfaces."""
        return SystemStatus(
            name="OrchFlow",
            version=__version__,
            status="ok",
            stage="bootstrap",
        )

    def get_configuration_summary(self) -> ConfigurationSummary:
        """Return a safe summary of runtime configuration details."""
        return ConfigurationSummary(
            environment=self._settings.env,
            api_base_url=self._settings.api_base_url,
            database_url=self._settings.normalized_database_url,
            database_dialect=self._settings.database_dialect,
            data_dir=str(self._settings.resolved_data_dir),
            runtime_dir=str(self._settings.resolved_runtime_dir),
            log_level=self._settings.log_level,
        )

    def get_database_status(self) -> DatabaseStatus:
        """Return the current persistence bootstrap connectivity state."""
        is_connected = check_database_connection(self._settings)
        return DatabaseStatus(
            status="ok" if is_connected else "error",
            is_connected=is_connected,
            database_url=self._settings.normalized_database_url,
            database_dialect=self._settings.database_dialect,
        )
