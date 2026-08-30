"""LiteLLM gateway client for OrchFlow AI assistance."""

from __future__ import annotations

from importlib.util import find_spec

from orchflow.application.ai_assistance import AIAssistanceStatus
from orchflow.infrastructure.config.settings import AppSettings

SUPPORTED_LITELLM_MODES = {"sdk", "gateway"}


class LiteLLMGatewayClient:
    """Safe configuration-level client for the LiteLLM gateway."""

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    def get_status(self) -> AIAssistanceStatus:
        """Return a safe status summary without invoking models or sending files."""
        sdk_available = find_spec("litellm") is not None
        api_key_configured = bool(self._settings.litellm_api_key.strip())
        mode = self._settings.litellm_mode.strip().lower()
        base_url = self._settings.litellm_base_url.strip()
        default_model = self._settings.litellm_default_model.strip()

        if not self._settings.ai_enabled:
            return AIAssistanceStatus(
                provider="litellm",
                status="disabled",
                enabled=False,
                mode=mode,
                base_url=base_url,
                default_model=default_model,
                timeout_seconds=self._settings.litellm_timeout_seconds,
                api_key_configured=api_key_configured,
                sdk_available=sdk_available,
                ready_for_requests=False,
                message="AI assistance is disabled by configuration.",
            )

        validation_errors = self._configuration_errors(
            mode=mode,
            base_url=base_url,
            default_model=default_model,
            sdk_available=sdk_available,
        )
        if validation_errors:
            return AIAssistanceStatus(
                provider="litellm",
                status="misconfigured",
                enabled=True,
                mode=mode,
                base_url=base_url,
                default_model=default_model,
                timeout_seconds=self._settings.litellm_timeout_seconds,
                api_key_configured=api_key_configured,
                sdk_available=sdk_available,
                ready_for_requests=False,
                message="; ".join(validation_errors),
            )

        return AIAssistanceStatus(
            provider="litellm",
            status="configured",
            enabled=True,
            mode=mode,
            base_url=base_url,
            default_model=default_model,
            timeout_seconds=self._settings.litellm_timeout_seconds,
            api_key_configured=api_key_configured,
            sdk_available=sdk_available,
            ready_for_requests=True,
            message=(
                "LiteLLM is configured for future AI assistance requests. "
                "No model request was executed."
            ),
        )

    def _configuration_errors(
        self,
        *,
        mode: str,
        base_url: str,
        default_model: str,
        sdk_available: bool,
    ) -> list[str]:
        errors: list[str] = []
        if mode not in SUPPORTED_LITELLM_MODES:
            errors.append("Unsupported LiteLLM mode.")
        if mode == "sdk" and not sdk_available:
            errors.append("LiteLLM SDK is not importable.")
        if mode == "gateway" and not base_url:
            errors.append("LiteLLM gateway base URL is required.")
        if not default_model:
            errors.append("LiteLLM default model is required.")
        if self._settings.litellm_timeout_seconds < 1:
            errors.append("LiteLLM timeout must be at least 1 second.")
        return errors
