"""LiteLLM gateway client for OrchFlow AI assistance."""

from __future__ import annotations

import json
import time
from importlib.util import find_spec
from json import JSONDecodeError
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from orchflow.application.ai_assistance import (
    AIAssistanceGatewayHealth,
    AIAssistanceModel,
    AIAssistanceModelCatalog,
    AIAssistanceStatus,
)
from orchflow.infrastructure.config.settings import AppSettings

SUPPORTED_LITELLM_MODES = {"sdk", "gateway"}


class HttpGet(Protocol):
    """Callable boundary used to perform safe LiteLLM gateway GET requests."""

    def __call__(
        self,
        url: str,
        headers: dict[str, str],
        timeout_seconds: int,
    ) -> tuple[int, str]: ...


def _default_http_get(
    url: str,
    headers: dict[str, str],
    timeout_seconds: int,
) -> tuple[int, str]:
    request = Request(url, headers=headers, method="GET")
    with urlopen(request, timeout=timeout_seconds) as response:
        body = response.read().decode("utf-8")
        return response.status, body


class LiteLLMGatewayClient:
    """Safe configuration-level client for the LiteLLM gateway."""

    def __init__(self, settings: AppSettings, http_get: HttpGet = _default_http_get) -> None:
        self._settings = settings
        self._http_get = http_get

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

    def check_health(self) -> AIAssistanceGatewayHealth:
        """Check LiteLLM gateway health without sending project context."""
        status = self.get_status()
        if not status.enabled:
            return AIAssistanceGatewayHealth(
                provider="litellm",
                status="disabled",
                enabled=False,
                mode=status.mode,
                base_url=status.base_url,
                checked=False,
                status_code=None,
                response_time_ms=None,
                message="AI assistance is disabled by configuration.",
            )
        if not status.ready_for_requests:
            return AIAssistanceGatewayHealth(
                provider="litellm",
                status="unhealthy",
                enabled=True,
                mode=status.mode,
                base_url=status.base_url,
                checked=False,
                status_code=None,
                response_time_ms=None,
                message=status.message,
            )
        if status.mode != "gateway":
            return AIAssistanceGatewayHealth(
                provider="litellm",
                status="unsupported",
                enabled=True,
                mode=status.mode,
                base_url=status.base_url,
                checked=False,
                status_code=None,
                response_time_ms=None,
                message="Gateway health checks require LiteLLM gateway mode.",
            )

        return self._request_gateway_health(status.base_url)

    def list_models(self) -> AIAssistanceModelCatalog:
        """List LiteLLM gateway models without sending project context."""
        status = self.get_status()
        if not status.enabled:
            return AIAssistanceModelCatalog(
                provider="litellm",
                enabled=False,
                mode=status.mode,
                base_url=status.base_url,
                default_model=status.default_model,
                models=(),
                supports_discovery=False,
                message="AI assistance is disabled by configuration.",
            )
        if not status.ready_for_requests:
            return AIAssistanceModelCatalog(
                provider="litellm",
                enabled=True,
                mode=status.mode,
                base_url=status.base_url,
                default_model=status.default_model,
                models=(),
                supports_discovery=False,
                message=status.message,
            )
        if status.mode != "gateway":
            return AIAssistanceModelCatalog(
                provider="litellm",
                enabled=True,
                mode=status.mode,
                base_url=status.base_url,
                default_model=status.default_model,
                models=(AIAssistanceModel(id=status.default_model),),
                supports_discovery=False,
                message=(
                    "Model discovery requires LiteLLM gateway mode; returning configured "
                    "default model only."
                ),
            )

        return self._request_gateway_models(status.base_url, status.default_model)

    def _request_gateway_health(self, base_url: str) -> AIAssistanceGatewayHealth:
        health_url = urljoin(f"{base_url.rstrip('/')}/", "health/readiness")
        started_at = time.perf_counter()
        try:
            status_code, _body = self._http_get(
                health_url,
                self._headers(),
                self._settings.litellm_timeout_seconds,
            )
        except HTTPError as error:
            return self._failed_health_response(
                base_url=base_url,
                status_code=error.code,
                response_time_ms=self._elapsed_ms(started_at),
                message=f"LiteLLM gateway health check failed with HTTP {error.code}.",
            )
        except (OSError, URLError) as error:
            return self._failed_health_response(
                base_url=base_url,
                status_code=None,
                response_time_ms=self._elapsed_ms(started_at),
                message=f"LiteLLM gateway health check failed: {error}",
            )

        is_healthy = 200 <= status_code < 300
        return AIAssistanceGatewayHealth(
            provider="litellm",
            status="healthy" if is_healthy else "unhealthy",
            enabled=True,
            mode="gateway",
            base_url=base_url,
            checked=True,
            status_code=status_code,
            response_time_ms=self._elapsed_ms(started_at),
            message=(
                "LiteLLM gateway health check succeeded."
                if is_healthy
                else f"LiteLLM gateway health check returned HTTP {status_code}."
            ),
        )

    def _request_gateway_models(
        self,
        base_url: str,
        default_model: str,
    ) -> AIAssistanceModelCatalog:
        models_url = urljoin(f"{base_url.rstrip('/')}/", "models")
        try:
            status_code, body = self._http_get(
                models_url,
                self._headers(),
                self._settings.litellm_timeout_seconds,
            )
        except HTTPError as error:
            return self._failed_model_catalog(
                base_url=base_url,
                default_model=default_model,
                message=f"LiteLLM model discovery failed with HTTP {error.code}.",
            )
        except (OSError, URLError) as error:
            return self._failed_model_catalog(
                base_url=base_url,
                default_model=default_model,
                message=f"LiteLLM model discovery failed: {error}",
            )

        if not 200 <= status_code < 300:
            return self._failed_model_catalog(
                base_url=base_url,
                default_model=default_model,
                message=f"LiteLLM model discovery returned HTTP {status_code}.",
            )

        try:
            models = self._parse_models(body)
        except JSONDecodeError:
            return self._failed_model_catalog(
                base_url=base_url,
                default_model=default_model,
                message="LiteLLM model discovery returned invalid JSON.",
            )
        return AIAssistanceModelCatalog(
            provider="litellm",
            enabled=True,
            mode="gateway",
            base_url=base_url,
            default_model=default_model,
            models=models,
            supports_discovery=True,
            message=f"Discovered {len(models)} LiteLLM model(s).",
        )

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        api_key = self._settings.litellm_api_key.strip()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _failed_health_response(
        self,
        *,
        base_url: str,
        status_code: int | None,
        response_time_ms: int,
        message: str,
    ) -> AIAssistanceGatewayHealth:
        return AIAssistanceGatewayHealth(
            provider="litellm",
            status="unhealthy",
            enabled=True,
            mode="gateway",
            base_url=base_url,
            checked=True,
            status_code=status_code,
            response_time_ms=response_time_ms,
            message=message,
        )

    def _failed_model_catalog(
        self,
        *,
        base_url: str,
        default_model: str,
        message: str,
    ) -> AIAssistanceModelCatalog:
        return AIAssistanceModelCatalog(
            provider="litellm",
            enabled=True,
            mode="gateway",
            base_url=base_url,
            default_model=default_model,
            models=(),
            supports_discovery=True,
            message=message,
        )

    @staticmethod
    def _parse_models(body: str) -> tuple[AIAssistanceModel, ...]:
        payload = json.loads(body)
        raw_models = payload.get("data", payload)
        if not isinstance(raw_models, list):
            return ()

        models: list[AIAssistanceModel] = []
        for raw_model in raw_models:
            if not isinstance(raw_model, dict):
                continue
            model_id = raw_model.get("id") or raw_model.get("model_name")
            if not isinstance(model_id, str) or not model_id:
                continue
            owned_by = raw_model.get("owned_by")
            models.append(
                AIAssistanceModel(
                    id=model_id,
                    owned_by=owned_by if isinstance(owned_by, str) else None,
                )
            )
        return tuple(models)

    @staticmethod
    def _elapsed_ms(started_at: float) -> int:
        return round((time.perf_counter() - started_at) * 1000)
