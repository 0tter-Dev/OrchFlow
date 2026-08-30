"""Tests for the OrchFlow-owned AI assistance boundary."""

from __future__ import annotations

from datetime import UTC, datetime

from orchflow.application.ai_assistance import (
    AIAssistanceService,
    AIAssistanceStatus,
    GetAIAssistanceStatusCommand,
)
from orchflow.domain.access_control import User, UserRole
from orchflow.infrastructure.ai.litellm_gateway import LiteLLMGatewayClient
from orchflow.infrastructure.config.settings import AppSettings


class FakeCurrentUserResolver:
    def get_current_user(self, token: str) -> User:
        assert token == "token"
        now = datetime.now(UTC)
        return User(
            id=123,
            username="operator",
            role=UserRole.MEMBER,
            is_active=True,
            created_at=now,
            updated_at=now,
            last_login_at=None,
        )


class FakeGateway:
    def get_status(self) -> AIAssistanceStatus:
        return AIAssistanceStatus(
            provider="litellm",
            status="disabled",
            enabled=False,
            mode="sdk",
            base_url="http://localhost:4000",
            default_model="ollama/llama2",
            timeout_seconds=60,
            api_key_configured=False,
            sdk_available=True,
            ready_for_requests=False,
            message="AI assistance is disabled by configuration.",
        )


class FakeAuditRecorder:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    def record_audit_event(
        self,
        *,
        actor_user_id: int | None,
        action: str,
        target_type: str,
        target_id: str | None,
        details: str | None,
    ) -> None:
        self.events.append(
            {
                "actor_user_id": actor_user_id,
                "action": action,
                "target_type": target_type,
                "target_id": target_id,
                "details": details,
            }
        )


def test_ai_assistance_service_reads_status_through_gateway_and_audits() -> None:
    audit_recorder = FakeAuditRecorder()
    service = AIAssistanceService(
        gateway=FakeGateway(),
        current_user_resolver=FakeCurrentUserResolver(),
        audit_recorder=audit_recorder,
    )

    status = service.get_status(GetAIAssistanceStatusCommand(token="token"))

    assert status.provider == "litellm"
    assert status.status == "disabled"
    assert audit_recorder.events == [
        {
            "actor_user_id": 123,
            "action": "ai_assistance.status.read",
            "target_type": "ai_assistance_gateway",
            "target_id": "litellm",
            "details": "status:disabled;enabled:false;mode:sdk;default_model:ollama/llama2",
        }
    ]


def test_litellm_gateway_client_defaults_to_disabled_without_requests() -> None:
    status = LiteLLMGatewayClient(AppSettings()).get_status()

    assert status.provider == "litellm"
    assert status.status == "disabled"
    assert status.enabled is False
    assert status.ready_for_requests is False
    assert status.default_model == "ollama/llama2"


def test_litellm_gateway_client_reports_enabled_configuration_without_invoking_model() -> None:
    status = LiteLLMGatewayClient(AppSettings(ai_enabled=True)).get_status()

    assert status.provider == "litellm"
    assert status.status == "configured"
    assert status.enabled is True
    assert status.ready_for_requests is True
    assert "No model request was executed." in status.message


def test_litellm_gateway_client_reports_invalid_enabled_configuration() -> None:
    status = LiteLLMGatewayClient(
        AppSettings(ai_enabled=True, litellm_default_model="", litellm_timeout_seconds=0)
    ).get_status()

    assert status.status == "misconfigured"
    assert status.ready_for_requests is False
    assert "default model is required" in status.message
    assert "timeout must be at least 1 second" in status.message
