"""FastAPI application factory for the OrchFlow backend bootstrap."""

from typing import Literal

from fastapi import FastAPI, Header, HTTPException, Query, status
from pydantic import BaseModel

from orchflow.application.access_control import (
    AccessControlError,
    AuthenticationError,
    AuthorizationError,
    LoginCommand,
    RegisterUserCommand,
    UpdateUserCommand,
    UserConflictError,
    UserNotFoundError,
)
from orchflow.application.audit_history import (
    AuditHistoryError,
    AuditHistoryValidationError,
    ListAuditEventsCommand,
)
from orchflow.application.lifecycle import ExecuteLifecycleCommand, LifecycleExecutionError
from orchflow.application.project_registry import (
    ProjectConflictError,
    ProjectMappingInput,
    ProjectOwnershipError,
    ProjectRegistryError,
    ProjectValidationError,
    RegisterProjectCommand,
    UpdateProjectOwnerCommand,
)
from orchflow.application.runtime_inspection import InspectRuntimeCommand
from orchflow.application.services import (
    create_access_control_service,
    create_audit_history_service,
    create_bootstrap_service,
    create_lifecycle_orchestration_service,
    create_project_registry_service,
    create_runtime_inspection_service,
)
from orchflow.domain.access_control import AuditEvent, User, UserRole
from orchflow.domain.lifecycle import LifecycleExecutionResult
from orchflow.domain.project_registry import CanonicalLifecycleAction, MappingSource, Project
from orchflow.domain.runtime_inspection import RuntimeInspectionSnapshot


class StatusResponse(BaseModel):
    name: str
    version: str
    status: str
    stage: str


class ConfigurationResponse(BaseModel):
    environment: str
    api_base_url: str
    database_url: str
    database_dialect: str
    data_dir: str
    runtime_dir: str
    log_level: str


class DatabaseResponse(BaseModel):
    status: str
    is_connected: bool
    database_url: str
    database_dialect: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: Literal["admin", "member"]
    is_active: bool


class AuditEventResponse(BaseModel):
    id: int
    actor_user_id: int | None
    action: str
    target_type: str
    target_id: str | None
    details: str | None
    created_at: str


class RegisterUserRequest(BaseModel):
    username: str
    password: str
    role: Literal["admin", "member"] | None = None


class UpdateUserRequest(BaseModel):
    role: Literal["admin", "member"] | None = None
    is_active: bool | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in_seconds: int


class ProjectMappingRequest(BaseModel):
    canonical_action: Literal["status", "start", "stop", "restart"]
    script_label: str
    source: Literal["user_defined", "imported", "ai_approved"] = "user_defined"


class RegisterProjectRequest(BaseModel):
    reference_name: str
    project_root_path: str
    lifecycle_script_path: str
    description: str | None = None
    mappings: list[ProjectMappingRequest] = []


class ProjectMappingResponse(BaseModel):
    canonical_action: Literal["status", "start", "stop", "restart"]
    script_label: str
    source: Literal["user_defined", "imported", "ai_approved"]
    configured_by_user_id: int


class ProjectResponse(BaseModel):
    id: int
    reference_name: str
    description: str | None
    project_root_path: str
    lifecycle_script_path: str
    created_by_user_id: int
    owner_user_ids: list[int]
    action_mappings: list[ProjectMappingResponse]


class LifecycleExecutionResponse(BaseModel):
    project_id: int
    canonical_action: Literal["status", "start", "stop", "restart"]
    command_identifier: str
    exit_code: int
    stdout: str
    stderr: str
    succeeded: bool
    runtime_status: str | None = None


class RuntimeProcessResponse(BaseModel):
    pid: int
    name: str
    cpu_seconds: float | None
    memory_bytes: int | None
    started_at: str | None


class RuntimeInspectionResponse(BaseModel):
    project_id: int
    status: str
    known_port: int | None
    application_url: str | None
    uptime_seconds: float | None
    process_snapshots: list[RuntimeProcessResponse]


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role.value,
        is_active=user.is_active,
    )


def _to_audit_event_response(event: AuditEvent) -> AuditEventResponse:
    return AuditEventResponse(
        id=event.id,
        actor_user_id=event.actor_user_id,
        action=event.action,
        target_type=event.target_type,
        target_id=event.target_id,
        details=event.details,
        created_at=event.created_at.isoformat(),
    )


def _to_project_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        reference_name=project.reference_name,
        description=project.description,
        project_root_path=project.project_root_path,
        lifecycle_script_path=project.lifecycle_script_path,
        created_by_user_id=project.created_by_user_id,
        owner_user_ids=list(project.owner_user_ids),
        action_mappings=[
            ProjectMappingResponse(
                canonical_action=mapping.canonical_action.value,
                script_label=mapping.script_label,
                source=mapping.source.value,
                configured_by_user_id=mapping.configured_by_user_id,
            )
            for mapping in project.action_mappings
        ],
    )


def _to_lifecycle_response(result: LifecycleExecutionResult) -> LifecycleExecutionResponse:
    return LifecycleExecutionResponse(
        project_id=result.project_id,
        canonical_action=result.canonical_action.value,
        command_identifier=result.command_identifier,
        exit_code=result.exit_code,
        stdout=result.stdout,
        stderr=result.stderr,
        succeeded=result.succeeded,
        runtime_status=(
            result.runtime_snapshot.status
            if result.runtime_snapshot is not None
            else None
        ),
    )


def _to_runtime_response(snapshot: RuntimeInspectionSnapshot) -> RuntimeInspectionResponse:
    return RuntimeInspectionResponse(
        project_id=snapshot.project_id,
        status=snapshot.status,
        known_port=snapshot.known_port,
        application_url=snapshot.application_url,
        uptime_seconds=snapshot.uptime_seconds,
        process_snapshots=[
            RuntimeProcessResponse(
                pid=process.pid,
                name=process.name,
                cpu_seconds=process.cpu_seconds,
                memory_bytes=process.memory_bytes,
                started_at=process.started_at.isoformat() if process.started_at else None,
            )
            for process in snapshot.process_snapshots
        ],
    )


def _extract_bearer_token(authorization: str | None) -> str | None:
    if authorization is None:
        return None
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must use the Bearer scheme.",
        )
    return authorization.removeprefix(prefix).strip()


def _map_access_control_error(error: AccessControlError) -> HTTPException:
    if isinstance(error, UserConflictError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    if isinstance(error, UserNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, AuthorizationError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    if isinstance(error, AuthenticationError):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


def _map_audit_history_error(error: AuditHistoryError | AuthorizationError) -> HTTPException:
    if isinstance(error, AuthorizationError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    if isinstance(error, AuditHistoryValidationError):
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


def _map_project_registry_error(
    error: ProjectRegistryError | AuthorizationError,
) -> HTTPException:
    if isinstance(error, ProjectConflictError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    if isinstance(error, ProjectOwnershipError):
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))
    if isinstance(error, ProjectValidationError):
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))
    if isinstance(error, AuthorizationError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


def _map_lifecycle_error(
    error: LifecycleExecutionError | AuthorizationError,
) -> HTTPException:
    if isinstance(error, AuthorizationError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(error),
    )


def create_app() -> FastAPI:
    bootstrap_service = create_bootstrap_service()
    access_control_service = create_access_control_service()
    audit_history_service = create_audit_history_service()
    project_registry_service = create_project_registry_service()
    lifecycle_service = create_lifecycle_orchestration_service()
    runtime_service = create_runtime_inspection_service()

    app = FastAPI(
        title="OrchFlow API",
        version=bootstrap_service.get_status().version,
        summary="Local-first project lifecycle orchestration API bootstrap.",
    )

    @app.get("/", response_model=StatusResponse, tags=["system"])
    def read_root() -> StatusResponse:
        return StatusResponse.model_validate(bootstrap_service.get_status(), from_attributes=True)

    @app.get("/health", response_model=StatusResponse, tags=["system"])
    def read_health() -> StatusResponse:
        return StatusResponse.model_validate(bootstrap_service.get_status(), from_attributes=True)

    @app.get("/system/config", response_model=ConfigurationResponse, tags=["system"])
    def read_configuration() -> ConfigurationResponse:
        return ConfigurationResponse.model_validate(
            bootstrap_service.get_configuration_summary(),
            from_attributes=True,
        )

    @app.get("/system/database", response_model=DatabaseResponse, tags=["system"])
    def read_database_status() -> DatabaseResponse:
        return DatabaseResponse.model_validate(
            bootstrap_service.get_database_status(),
            from_attributes=True,
        )

    @app.post(
        "/auth/register",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["auth"],
    )
    def register_user(
        payload: RegisterUserRequest,
        authorization: str | None = Header(default=None),
    ) -> UserResponse:
        requested_role = UserRole(payload.role) if payload.role is not None else None
        actor_token = _extract_bearer_token(authorization)
        try:
            user = access_control_service.register_user(
                RegisterUserCommand(
                    username=payload.username,
                    password=payload.password,
                    requested_role=requested_role,
                    actor_token=actor_token,
                )
            )
        except AccessControlError as error:
            raise _map_access_control_error(error) from error
        return _to_user_response(user)

    @app.post("/auth/login", response_model=AccessTokenResponse, tags=["auth"])
    def login(payload: LoginRequest) -> AccessTokenResponse:
        try:
            token = access_control_service.login(
                LoginCommand(username=payload.username, password=payload.password)
            )
        except AccessControlError as error:
            raise _map_access_control_error(error) from error
        return AccessTokenResponse.model_validate(token, from_attributes=True)

    @app.get("/auth/me", response_model=UserResponse, tags=["auth"])
    def me(authorization: str | None = Header(default=None)) -> UserResponse:
        token = _extract_bearer_token(authorization)
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token.",
            )
        try:
            user = access_control_service.get_current_user(token)
        except AccessControlError as error:
            raise _map_access_control_error(error) from error
        return _to_user_response(user)

    @app.get("/auth/users", response_model=list[UserResponse], tags=["auth"])
    def list_users(authorization: str | None = Header(default=None)) -> list[UserResponse]:
        token = _extract_bearer_token(authorization)
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token.",
            )
        try:
            users = access_control_service.list_users(token)
        except AccessControlError as error:
            raise _map_access_control_error(error) from error
        return [_to_user_response(user) for user in users]

    @app.patch("/auth/users/{user_id}", response_model=UserResponse, tags=["auth"])
    def update_user(
        user_id: int,
        payload: UpdateUserRequest,
        authorization: str | None = Header(default=None),
    ) -> UserResponse:
        token = _extract_bearer_token(authorization)
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token.",
            )
        try:
            user = access_control_service.update_user(
                UpdateUserCommand(
                    token=token,
                    user_id=user_id,
                    role=UserRole(payload.role) if payload.role is not None else None,
                    is_active=payload.is_active,
                )
            )
        except AccessControlError as error:
            raise _map_access_control_error(error) from error
        return _to_user_response(user)

    @app.get("/audit/events", response_model=list[AuditEventResponse], tags=["audit"])
    def list_audit_events(
        authorization: str | None = Header(default=None),
        limit: int = Query(default=25, ge=1, le=100),
    ) -> list[AuditEventResponse]:
        token = _extract_bearer_token(authorization)
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token.",
            )
        try:
            events = audit_history_service.list_recent_events(
                ListAuditEventsCommand(token=token, limit=limit)
            )
        except (AuditHistoryError, AuthorizationError) as error:
            raise _map_audit_history_error(error) from error
        return [_to_audit_event_response(event) for event in events]

    @app.post(
        "/projects",
        response_model=ProjectResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["projects"],
    )
    def register_project(
        payload: RegisterProjectRequest,
        authorization: str | None = Header(default=None),
    ) -> ProjectResponse:
        token = _extract_bearer_token(authorization)
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token.",
            )
        try:
            project = project_registry_service.register_project(
                RegisterProjectCommand(
                    token=token,
                    reference_name=payload.reference_name,
                    project_root_path=payload.project_root_path,
                    lifecycle_script_path=payload.lifecycle_script_path,
                    description=payload.description,
                    mappings=tuple(
                        ProjectMappingInput(
                            canonical_action=CanonicalLifecycleAction(mapping.canonical_action),
                            script_label=mapping.script_label,
                            source=MappingSource(mapping.source),
                        )
                        for mapping in payload.mappings
                    ),
                )
            )
        except (ProjectRegistryError, AuthorizationError) as error:
            raise _map_project_registry_error(error) from error
        return _to_project_response(project)

    @app.get("/projects", response_model=list[ProjectResponse], tags=["projects"])
    def list_projects(authorization: str | None = Header(default=None)) -> list[ProjectResponse]:
        token = _extract_bearer_token(authorization)
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token.",
            )
        try:
            projects = project_registry_service.list_projects(token)
        except (ProjectRegistryError, AuthorizationError) as error:
            raise _map_project_registry_error(error) from error
        return [_to_project_response(project) for project in projects]

    @app.get("/projects/{project_id}", response_model=ProjectResponse, tags=["projects"])
    def get_project(
        project_id: int,
        authorization: str | None = Header(default=None),
    ) -> ProjectResponse:
        token = _extract_bearer_token(authorization)
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token.",
            )
        try:
            project = project_registry_service.get_project(token, project_id)
        except (ProjectRegistryError, AuthorizationError) as error:
            raise _map_project_registry_error(error) from error
        return _to_project_response(project)

    @app.post(
        "/projects/{project_id}/owners/{user_id}",
        response_model=ProjectResponse,
        tags=["projects"],
    )
    def add_project_owner(
        project_id: int,
        user_id: int,
        authorization: str | None = Header(default=None),
    ) -> ProjectResponse:
        token = _extract_bearer_token(authorization)
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token.",
            )
        try:
            project = project_registry_service.add_project_owner(
                UpdateProjectOwnerCommand(token=token, project_id=project_id, user_id=user_id)
            )
        except (ProjectRegistryError, AuthorizationError) as error:
            raise _map_project_registry_error(error) from error
        return _to_project_response(project)

    @app.delete(
        "/projects/{project_id}/owners/{user_id}",
        response_model=ProjectResponse,
        tags=["projects"],
    )
    def remove_project_owner(
        project_id: int,
        user_id: int,
        authorization: str | None = Header(default=None),
    ) -> ProjectResponse:
        token = _extract_bearer_token(authorization)
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token.",
            )
        try:
            project = project_registry_service.remove_project_owner(
                UpdateProjectOwnerCommand(token=token, project_id=project_id, user_id=user_id)
            )
        except (ProjectRegistryError, AuthorizationError) as error:
            raise _map_project_registry_error(error) from error
        return _to_project_response(project)

    @app.post(
        "/projects/{project_id}/lifecycle/{action}",
        response_model=LifecycleExecutionResponse,
        tags=["lifecycle"],
    )
    def execute_lifecycle_action(
        project_id: int,
        action: Literal["status", "start", "stop", "restart"],
        authorization: str | None = Header(default=None),
    ) -> LifecycleExecutionResponse:
        token = _extract_bearer_token(authorization)
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token.",
            )
        try:
            result = lifecycle_service.execute_action(
                ExecuteLifecycleCommand(
                    token=token,
                    project_id=project_id,
                    action=CanonicalLifecycleAction(action),
                )
            )
        except (LifecycleExecutionError, AuthorizationError) as error:
            raise _map_lifecycle_error(error) from error
        return _to_lifecycle_response(result)

    @app.get(
        "/projects/{project_id}/runtime",
        response_model=RuntimeInspectionResponse,
        tags=["runtime"],
    )
    def inspect_runtime(
        project_id: int,
        authorization: str | None = Header(default=None),
    ) -> RuntimeInspectionResponse:
        token = _extract_bearer_token(authorization)
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token.",
            )
        snapshot = runtime_service.inspect_runtime(
            InspectRuntimeCommand(token=token, project_id=project_id)
        )
        return _to_runtime_response(snapshot)

    return app
