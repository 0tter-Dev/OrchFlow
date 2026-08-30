"""Tests for the OrchFlow-owned AI assistance boundary."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from orchflow.application.ai_assistance import (
    AIAnalysisProposal,
    AIAnalysisProposalReview,
    AIAnalysisProposalReviewDecision,
    AIAssistanceGatewayHealth,
    AIAssistanceModel,
    AIAssistanceModelCatalog,
    AIAssistancePromptMessage,
    AIAssistanceService,
    AIAssistanceStatus,
    AuthorizedContextManifest,
    CheckAIAssistanceGatewayHealthCommand,
    CreateAnalysisProposalCommand,
    CreateAuthorizedContextManifestCommand,
    GetAIAssistanceStatusCommand,
    GetAnalysisProposalCommand,
    GetAuthorizedContextManifestCommand,
    ListAIAssistanceModelsCommand,
    ProposedLifecycleActionMapping,
    ReviewAnalysisProposalCommand,
)
from orchflow.domain.access_control import User, UserRole
from orchflow.domain.project_registry import Project
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


class FakeProjectResolver:
    def __init__(self, project_root_path: Path) -> None:
        now = datetime.now(UTC)
        self.project = Project(
            id=456,
            reference_name="sample",
            description=None,
            project_root_path=str(project_root_path),
            lifecycle_script_path=str(project_root_path / "control.bat"),
            created_by_user_id=123,
            created_at=now,
            updated_at=now,
            owner_user_ids=(123,),
            action_mappings=(),
            lifecycle_function_decisions=(),
        )

    def get_project(self, token: str, project_id: int) -> Project:
        assert token == "token"
        assert project_id == self.project.id
        return self.project


class FakeGateway:
    def __init__(self, *, ready_for_requests: bool = False) -> None:
        self.ready_for_requests = ready_for_requests
        self.messages: tuple[AIAssistancePromptMessage, ...] = ()

    def get_status(self) -> AIAssistanceStatus:
        return AIAssistanceStatus(
            provider="litellm",
            status="configured" if self.ready_for_requests else "disabled",
            enabled=self.ready_for_requests,
            mode="sdk",
            base_url="http://localhost:4000",
            default_model="ollama/llama2",
            timeout_seconds=60,
            api_key_configured=False,
            sdk_available=True,
            ready_for_requests=self.ready_for_requests,
            message=(
                "LiteLLM is configured for future AI assistance requests. "
                "No model request was executed."
                if self.ready_for_requests
                else "AI assistance is disabled by configuration."
            ),
        )

    def check_health(self) -> AIAssistanceGatewayHealth:
        return AIAssistanceGatewayHealth(
            provider="litellm",
            status="disabled",
            enabled=False,
            mode="sdk",
            base_url="http://localhost:4000",
            checked=False,
            status_code=None,
            response_time_ms=None,
            message="AI assistance is disabled by configuration.",
        )

    def list_models(self) -> AIAssistanceModelCatalog:
        return AIAssistanceModelCatalog(
            provider="litellm",
            enabled=False,
            mode="sdk",
            base_url="http://localhost:4000",
            default_model="ollama/llama2",
            models=(),
            supports_discovery=False,
            message="AI assistance is disabled by configuration.",
        )

    def generate_completion(
        self,
        *,
        model: str,
        messages: tuple[AIAssistancePromptMessage, ...],
    ) -> str:
        assert model == "ollama/llama3"
        self.messages = messages
        return (
            '{"lifecycle_strategy":"Use first-argument dispatch for canonical actions.",'
            '"runtime_hints":["APP_PORT may be declared in control.bat."],'
            '"candidate_script_content":"@echo off\\r\\nif /I \\"%~1\\"==\\"STATUS\\" '
            'echo ok & exit /b 0\\r\\nif /I \\"%~1\\"==\\"START\\" echo ok & exit /b 0\\r\\n'
            'if /I \\"%~1\\"==\\"STOP\\" echo ok & exit /b 0\\r\\n'
            'if /I \\"%~1\\"==\\"RESTART\\" echo ok & exit /b 0\\r\\n",'
            '"action_mappings":[{"canonical_action":"status","script_label":"STATUS",'
            '"rationale":"Canonical status handler."}],'
            '"warnings":["Review before applying."]}'
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


class FakeManifestRepository:
    def __init__(self) -> None:
        self.manifest: AuthorizedContextManifest | None = None
        self.proposal: AIAnalysisProposal | None = None
        self.review: AIAnalysisProposalReview | None = None

    def create_authorized_context_manifest(
        self,
        *,
        project_id: int,
        requested_by_user_id: int,
        selected_model: str,
        intended_operation: str,
        project_root_path: str,
        include_patterns: tuple[str, ...],
        exclude_patterns: tuple[str, ...],
        included_paths: tuple[str, ...],
        excluded_paths: tuple[str, ...],
        ignored_paths: tuple[str, ...],
        secret_filter_rules: tuple[str, ...],
        max_file_size_bytes: int,
        max_total_bytes: int,
        total_included_bytes: int,
    ) -> AuthorizedContextManifest:
        self.manifest = AuthorizedContextManifest(
            id=1,
            project_id=project_id,
            requested_by_user_id=requested_by_user_id,
            selected_model=selected_model,
            intended_operation=intended_operation,
            project_root_path=project_root_path,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            included_paths=included_paths,
            excluded_paths=excluded_paths,
            ignored_paths=ignored_paths,
            secret_filter_rules=secret_filter_rules,
            max_file_size_bytes=max_file_size_bytes,
            max_total_bytes=max_total_bytes,
            total_included_bytes=total_included_bytes,
            created_at=datetime.now(UTC),
        )
        return self.manifest

    def get_authorized_context_manifest(
        self,
        manifest_id: int,
    ) -> AuthorizedContextManifest | None:
        assert manifest_id == 1
        return self.manifest

    def create_analysis_proposal(
        self,
        *,
        manifest_id: int,
        project_id: int,
        requested_by_user_id: int,
        selected_model: str,
        intended_operation: str,
        lifecycle_strategy: str,
        runtime_hints: tuple[str, ...],
        candidate_script_content: str,
        action_mappings: tuple[ProposedLifecycleActionMapping, ...],
        warnings: tuple[str, ...],
    ) -> AIAnalysisProposal:
        self.proposal = AIAnalysisProposal(
            id=2,
            manifest_id=manifest_id,
            project_id=project_id,
            requested_by_user_id=requested_by_user_id,
            selected_model=selected_model,
            intended_operation=intended_operation,
            lifecycle_strategy=lifecycle_strategy,
            runtime_hints=runtime_hints,
            candidate_script_content=candidate_script_content,
            action_mappings=action_mappings,
            warnings=warnings,
            created_at=datetime.now(UTC),
        )
        return self.proposal

    def get_analysis_proposal(
        self,
        proposal_id: int,
    ) -> AIAnalysisProposal | None:
        assert proposal_id == 2
        return self.proposal

    def create_analysis_proposal_review(
        self,
        *,
        proposal_id: int,
        project_id: int,
        reviewer_user_id: int,
        decision: AIAnalysisProposalReviewDecision,
        validation_status: str,
        validation_errors: tuple[str, ...],
        reviewer_notes: str | None,
    ) -> AIAnalysisProposalReview:
        self.review = AIAnalysisProposalReview(
            id=3,
            proposal_id=proposal_id,
            project_id=project_id,
            reviewer_user_id=reviewer_user_id,
            decision=decision,
            validation_status=validation_status,
            validation_errors=validation_errors,
            reviewer_notes=reviewer_notes,
            created_at=datetime.now(UTC),
        )
        return self.review

    def get_analysis_proposal_review_for_proposal(
        self,
        proposal_id: int,
    ) -> AIAnalysisProposalReview | None:
        assert proposal_id == 2
        return self.review


def _build_service(
    *,
    project_root_path: Path | None = None,
    gateway: FakeGateway | None = None,
    audit_recorder: FakeAuditRecorder | None = None,
    manifest_repository: FakeManifestRepository | None = None,
) -> AIAssistanceService:
    root_path = project_root_path or Path.cwd()
    return AIAssistanceService(
        gateway=gateway or FakeGateway(),
        current_user_resolver=FakeCurrentUserResolver(),
        audit_recorder=audit_recorder or FakeAuditRecorder(),
        project_resolver=FakeProjectResolver(root_path),
        manifest_repository=manifest_repository or FakeManifestRepository(),
    )


def test_ai_assistance_service_reads_status_through_gateway_and_audits() -> None:
    audit_recorder = FakeAuditRecorder()
    service = _build_service(audit_recorder=audit_recorder)

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


def test_ai_assistance_service_checks_gateway_health_and_audits() -> None:
    audit_recorder = FakeAuditRecorder()
    service = _build_service(audit_recorder=audit_recorder)

    health = service.check_gateway_health(
        CheckAIAssistanceGatewayHealthCommand(token="token")
    )

    assert health.status == "disabled"
    assert audit_recorder.events == [
        {
            "actor_user_id": 123,
            "action": "ai_assistance.gateway.health",
            "target_type": "ai_assistance_gateway",
            "target_id": "litellm",
            "details": (
                "status:disabled;enabled:false;mode:sdk;"
                "checked:false;status_code:None"
            ),
        }
    ]


def test_ai_assistance_service_lists_models_and_audits() -> None:
    audit_recorder = FakeAuditRecorder()
    service = _build_service(audit_recorder=audit_recorder)

    catalog = service.list_models(ListAIAssistanceModelsCommand(token="token"))

    assert catalog.models == ()
    assert audit_recorder.events == [
        {
            "actor_user_id": 123,
            "action": "ai_assistance.models.list",
            "target_type": "ai_assistance_gateway",
            "target_id": "litellm",
            "details": (
                "enabled:false;mode:sdk;supports_discovery:false;model_count:0"
            ),
        }
    ]


def test_ai_assistance_service_creates_authorized_context_manifest(
    tmp_path: Path,
) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / ".env").write_text("TOKEN=secret\n", encoding="utf-8")
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "bundle.js").write_text("generated\n", encoding="utf-8")
    audit_recorder = FakeAuditRecorder()
    manifest_repository = FakeManifestRepository()
    service = _build_service(
        project_root_path=tmp_path,
        audit_recorder=audit_recorder,
        manifest_repository=manifest_repository,
    )

    manifest = service.create_authorized_context_manifest(
        CreateAuthorizedContextManifestCommand(
            token="token",
            project_id=456,
            selected_model="ollama/llama3",
            intended_operation="improve_lifecycle_script",
            include_patterns=("src/*.py",),
        )
    )

    assert manifest.included_paths == ("src/app.py",)
    assert ".env" in manifest.ignored_paths
    assert "dist/bundle.js" in manifest.ignored_paths
    assert manifest.secret_filter_rules
    assert manifest.total_included_bytes == (tmp_path / "src" / "app.py").stat().st_size
    assert audit_recorder.events[-1]["action"] == "ai_assistance.context_manifest.create"

    persisted_manifest = service.get_authorized_context_manifest(
        GetAuthorizedContextManifestCommand(token="token", manifest_id=1)
    )

    assert persisted_manifest.id == manifest.id
    assert audit_recorder.events[-1]["action"] == "ai_assistance.context_manifest.read"


def test_ai_assistance_service_creates_reviewable_analysis_proposal(
    tmp_path: Path,
) -> None:
    (tmp_path / "app.py").write_text("print('approved context')\n", encoding="utf-8")
    (tmp_path / "control.bat").write_text("@echo off\r\n", encoding="utf-8")
    audit_recorder = FakeAuditRecorder()
    manifest_repository = FakeManifestRepository()
    gateway = FakeGateway(ready_for_requests=True)
    service = _build_service(
        project_root_path=tmp_path,
        gateway=gateway,
        audit_recorder=audit_recorder,
        manifest_repository=manifest_repository,
    )
    manifest = service.create_authorized_context_manifest(
        CreateAuthorizedContextManifestCommand(
            token="token",
            project_id=456,
            selected_model="ollama/llama3",
            intended_operation="improve_lifecycle_script",
            include_patterns=("app.py",),
        )
    )

    proposal = service.create_analysis_proposal(
        CreateAnalysisProposalCommand(
            token="token",
            manifest_id=manifest.id,
            user_instructions="Prefer canonical labels.",
        )
    )

    assert proposal.manifest_id == manifest.id
    assert proposal.lifecycle_strategy == "Use first-argument dispatch for canonical actions."
    assert proposal.runtime_hints == ("APP_PORT may be declared in control.bat.",)
    assert proposal.action_mappings[0].canonical_action == "status"
    assert proposal.action_mappings[0].script_label == "STATUS"
    assert "approved context" in gateway.messages[1].content
    assert "control.bat" not in proposal.candidate_script_content
    assert (tmp_path / "control.bat").read_text(encoding="utf-8").split() == [
        "@echo",
        "off",
    ]
    assert audit_recorder.events[-1]["action"] == "ai_assistance.analysis_proposal.create"

    persisted_proposal = service.get_analysis_proposal(
        GetAnalysisProposalCommand(token="token", proposal_id=2)
    )

    assert persisted_proposal.id == proposal.id
    assert audit_recorder.events[-1]["action"] == "ai_assistance.analysis_proposal.read"


def test_ai_assistance_service_approves_valid_analysis_proposal(
    tmp_path: Path,
) -> None:
    (tmp_path / "app.py").write_text("print('approved context')\n", encoding="utf-8")
    audit_recorder = FakeAuditRecorder()
    manifest_repository = FakeManifestRepository()
    service = _build_service(
        project_root_path=tmp_path,
        gateway=FakeGateway(ready_for_requests=True),
        audit_recorder=audit_recorder,
        manifest_repository=manifest_repository,
    )
    manifest = service.create_authorized_context_manifest(
        CreateAuthorizedContextManifestCommand(
            token="token",
            project_id=456,
            selected_model="ollama/llama3",
            intended_operation="improve_lifecycle_script",
            include_patterns=("app.py",),
        )
    )
    proposal = service.create_analysis_proposal(
        CreateAnalysisProposalCommand(token="token", manifest_id=manifest.id)
    )

    review = service.review_analysis_proposal(
        ReviewAnalysisProposalCommand(
            token="token",
            proposal_id=proposal.id,
            decision="approved",
            reviewer_notes="Looks good.",
        )
    )

    assert review.decision == "approved"
    assert review.validation_status == "valid"
    assert review.validation_errors == ()
    assert review.reviewer_notes == "Looks good."
    assert audit_recorder.events[-1]["action"] == "ai_assistance.analysis_proposal.review"


def test_ai_assistance_service_rejects_invalid_analysis_proposal(
    tmp_path: Path,
) -> None:
    audit_recorder = FakeAuditRecorder()
    manifest_repository = FakeManifestRepository()
    now = datetime.now(UTC)
    manifest_repository.proposal = AIAnalysisProposal(
        id=2,
        manifest_id=1,
        project_id=456,
        requested_by_user_id=123,
        selected_model="ollama/llama3",
        intended_operation="improve_lifecycle_script",
        lifecycle_strategy="Missing dispatch handlers.",
        runtime_hints=(),
        candidate_script_content="@echo off\r\necho no dispatch\r\n",
        action_mappings=(),
        warnings=(),
        created_at=now,
    )
    service = _build_service(
        project_root_path=tmp_path,
        audit_recorder=audit_recorder,
        manifest_repository=manifest_repository,
    )

    review = service.review_analysis_proposal(
        ReviewAnalysisProposalCommand(
            token="token",
            proposal_id=2,
            decision="rejected",
            reviewer_notes="Needs a dispatcher.",
        )
    )

    assert review.decision == "rejected"
    assert review.validation_status == "invalid"
    assert review.validation_errors
    assert audit_recorder.events[-1]["action"] == "ai_assistance.analysis_proposal.review"


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


def test_litellm_gateway_health_is_disabled_without_request() -> None:
    calls: list[str] = []

    def http_get(url: str, headers: dict[str, str], timeout_seconds: int) -> tuple[int, str]:
        calls.append(url)
        return 200, "{}"

    health = LiteLLMGatewayClient(AppSettings(), http_get=http_get).check_health()

    assert health.status == "disabled"
    assert health.checked is False
    assert calls == []


def test_litellm_gateway_health_checks_gateway_mode() -> None:
    calls: list[tuple[str, dict[str, str], int]] = []

    def http_get(url: str, headers: dict[str, str], timeout_seconds: int) -> tuple[int, str]:
        calls.append((url, headers, timeout_seconds))
        return 200, "{}"

    health = LiteLLMGatewayClient(
        AppSettings(
            ai_enabled=True,
            litellm_mode="gateway",
            litellm_base_url="http://litellm.local",
            litellm_api_key="secret",
            litellm_timeout_seconds=7,
        ),
        http_get=http_get,
    ).check_health()

    assert health.status == "healthy"
    assert health.checked is True
    assert health.status_code == 200
    assert calls == [
        (
            "http://litellm.local/health/readiness",
            {"Accept": "application/json", "Authorization": "Bearer secret"},
            7,
        )
    ]


def test_litellm_model_discovery_returns_default_model_for_sdk_mode() -> None:
    catalog = LiteLLMGatewayClient(AppSettings(ai_enabled=True)).list_models()

    assert catalog.supports_discovery is False
    assert catalog.models == (AIAssistanceModel(id="ollama/llama2"),)


def test_litellm_model_discovery_reads_openai_compatible_gateway_response() -> None:
    def http_get(url: str, headers: dict[str, str], timeout_seconds: int) -> tuple[int, str]:
        assert url == "http://litellm.local/models"
        return (
            200,
            '{"data":[{"id":"ollama/llama3","owned_by":"local"},'
            '{"model_name":"openai/gpt-4.1"}]}',
        )

    catalog = LiteLLMGatewayClient(
        AppSettings(
            ai_enabled=True,
            litellm_mode="gateway",
            litellm_base_url="http://litellm.local",
            litellm_default_model="ollama/llama3",
        ),
        http_get=http_get,
    ).list_models()

    assert catalog.supports_discovery is True
    assert catalog.models == (
        AIAssistanceModel(id="ollama/llama3", owned_by="local"),
        AIAssistanceModel(id="openai/gpt-4.1"),
    )
