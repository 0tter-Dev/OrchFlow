"""Typer application for the OrchFlow backend bootstrap."""

from typing import Annotated

import typer

from orchflow.application.access_control import (
    AccessControlError,
    LoginCommand,
    RegisterUserCommand,
    UpdateUserCommand,
)
from orchflow.application.audit_history import (
    AuditHistoryError,
    ListAuditEventsCommand,
)
from orchflow.application.bootstrap import BootstrapStatusService
from orchflow.application.lifecycle import ExecuteLifecycleCommand, LifecycleExecutionError
from orchflow.application.project_registry import (
    ProjectMappingInput,
    ProjectOwnershipError,
    ProjectRegistryError,
    RegisterProjectCommand,
    ReloadProjectCommand,
    ReloadProjectsCommand,
    UpdateLifecycleFunctionConfigurationCommand,
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
from orchflow.domain.access_control import AccessToken, UserRole
from orchflow.domain.project_registry import CanonicalLifecycleAction, MappingSource
from orchflow.external.presenters import (
    render_audit_event,
    render_lifecycle_result,
    render_project,
    render_project_reload_result,
    render_runtime_snapshot,
    render_user,
)

app = typer.Typer(
    add_completion=False,
    help="OrchFlow command-line interface.",
    no_args_is_help=True,
)
auth_app = typer.Typer(help="Authentication and authorization commands.")
project_app = typer.Typer(help="Project registration and visibility commands.")
lifecycle_app = typer.Typer(help="Lifecycle orchestration commands.")
app.add_typer(auth_app, name="auth")
app.add_typer(project_app, name="project")
app.add_typer(lifecycle_app, name="lifecycle")
runtime_app = typer.Typer(help="Runtime inspection commands.")
app.add_typer(runtime_app, name="runtime")
audit_app = typer.Typer(help="Operational audit history commands.")
app.add_typer(audit_app, name="audit")


def _render_status(service: BootstrapStatusService) -> str:
    status_data = service.get_status()
    return (
        f"{status_data.name} {status_data.version}\n"
        f"status: {status_data.status}\n"
        f"stage: {status_data.stage}"
    )


def _render_configuration(service: BootstrapStatusService) -> str:
    summary = service.get_configuration_summary()
    return (
        f"environment: {summary.environment}\n"
        f"api_base_url: {summary.api_base_url}\n"
        f"database_url: {summary.database_url}\n"
        f"database_dialect: {summary.database_dialect}\n"
        f"data_dir: {summary.data_dir}\n"
        f"runtime_dir: {summary.runtime_dir}\n"
        f"log_level: {summary.log_level}"
    )


def _render_database_status(service: BootstrapStatusService) -> str:
    database_status = service.get_database_status()
    return (
        f"status: {database_status.status}\n"
        f"is_connected: {str(database_status.is_connected).lower()}\n"
        f"database_url: {database_status.database_url}\n"
        f"database_dialect: {database_status.database_dialect}"
    )


def _render_token(token: AccessToken) -> str:
    return (
        f"access_token: {token.access_token}\n"
        f"token_type: {token.token_type}\n"
        f"expires_in_seconds: {token.expires_in_seconds}"
    )


def _build_mapping_inputs(
    map_status: str | None,
    map_start: str | None,
    map_stop: str | None,
    map_restart: str | None,
) -> tuple[ProjectMappingInput, ...]:
    mapping_values = (
        (CanonicalLifecycleAction.STATUS, map_status),
        (CanonicalLifecycleAction.START, map_start),
        (CanonicalLifecycleAction.STOP, map_stop),
        (CanonicalLifecycleAction.RESTART, map_restart),
    )
    return tuple(
        ProjectMappingInput(
            canonical_action=canonical_action,
            script_label=script_label,
            source=MappingSource.USER_DEFINED,
        )
        for canonical_action, script_label in mapping_values
        if script_label is not None
    )


def _build_unconfigured_actions(
    status_unconfigured: bool,
    start_unconfigured: bool,
    stop_unconfigured: bool,
    restart_unconfigured: bool,
) -> tuple[CanonicalLifecycleAction, ...]:
    unconfigured_values = (
        (CanonicalLifecycleAction.STATUS, status_unconfigured),
        (CanonicalLifecycleAction.START, start_unconfigured),
        (CanonicalLifecycleAction.STOP, stop_unconfigured),
        (CanonicalLifecycleAction.RESTART, restart_unconfigured),
    )
    return tuple(
        canonical_action
        for canonical_action, is_unconfigured in unconfigured_values
        if is_unconfigured
    )


def _exit_with_error(error: Exception) -> None:
    typer.echo(f"error: {error}", err=True)
    raise typer.Exit(code=1)


def _execute_lifecycle_action(
    *,
    token: str,
    project_id: int,
    action: CanonicalLifecycleAction,
) -> None:
    service = create_lifecycle_orchestration_service()
    try:
        result = service.execute_action(
            ExecuteLifecycleCommand(
                token=token,
                project_id=project_id,
                action=action,
            )
        )
    except (LifecycleExecutionError, ProjectRegistryError, AccessControlError) as error:
        _exit_with_error(error)
    typer.echo(render_lifecycle_result(result))


@app.command("info")
def info() -> None:
    """Show the current application bootstrap metadata."""
    typer.echo(_render_status(create_bootstrap_service()))


@app.command("health")
def health() -> None:
    """Show the current bootstrap health state."""
    typer.echo(_render_status(create_bootstrap_service()))


@app.command("config")
def config() -> None:
    """Show the current safe runtime configuration summary."""
    typer.echo(_render_configuration(create_bootstrap_service()))


@app.command("database")
def database() -> None:
    """Show the current database connectivity summary."""
    typer.echo(_render_database_status(create_bootstrap_service()))


@auth_app.command("register")
def register(
    username: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    role: str | None = typer.Option(default=None),
    token: str | None = typer.Option(default=None),
) -> None:
    """Register a new OrchFlow user."""
    service = create_access_control_service()
    requested_role = UserRole(role) if role is not None else None
    try:
        user = service.register_user(
            RegisterUserCommand(
                username=username,
                password=password,
                requested_role=requested_role,
                actor_token=token,
            )
        )
    except AccessControlError as error:
        _exit_with_error(error)
    typer.echo(render_user(user))


@auth_app.command("login")
def login(
    username: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True),
) -> None:
    """Authenticate a user and emit a bearer token."""
    service = create_access_control_service()
    try:
        token = service.login(LoginCommand(username=username, password=password))
    except AccessControlError as error:
        _exit_with_error(error)
    typer.echo(_render_token(token))


@auth_app.command("me")
def me(token: str = typer.Option(...)) -> None:
    """Show the currently authenticated user."""
    service = create_access_control_service()
    try:
        user = service.get_current_user(token)
    except AccessControlError as error:
        _exit_with_error(error)
    typer.echo(render_user(user))


@auth_app.command("users")
def users(token: str = typer.Option(...)) -> None:
    """List users as an authenticated admin."""
    service = create_access_control_service()
    try:
        current_users = service.list_users(token)
    except AccessControlError as error:
        _exit_with_error(error)
    for user in current_users:
        typer.echo(render_user(user))
        typer.echo("")


@auth_app.command("update-user")
def update_user(
    token: str = typer.Option(...),
    user_id: int = typer.Option(...),
    role: str | None = typer.Option(default=None),
    is_active: bool | None = typer.Option(default=None),
) -> None:
    """Update a user's role or activation state as an authenticated admin."""
    service = create_access_control_service()
    requested_role = UserRole(role) if role is not None else None
    try:
        user = service.update_user(
            UpdateUserCommand(
                token=token,
                user_id=user_id,
                role=requested_role,
                is_active=is_active,
            )
        )
    except AccessControlError as error:
        _exit_with_error(error)
    typer.echo(render_user(user))


@project_app.command("register")
def register_project(
    token: str = typer.Option(...),
    reference_name: str = typer.Option(...),
    project_root_path: str = typer.Option(...),
    lifecycle_script_path: str = typer.Option(...),
    description: str | None = typer.Option(default=None),
    map_status: str | None = typer.Option(default=None),
    map_start: str | None = typer.Option(default=None),
    map_stop: str | None = typer.Option(default=None),
    map_restart: str | None = typer.Option(default=None),
) -> None:
    """Register a project from an existing lifecycle .bat file."""
    service = create_project_registry_service()
    mappings = _build_mapping_inputs(map_status, map_start, map_stop, map_restart)
    try:
        project = service.register_project(
            RegisterProjectCommand(
                token=token,
                reference_name=reference_name,
                project_root_path=project_root_path,
                lifecycle_script_path=lifecycle_script_path,
                description=description,
                mappings=mappings,
            )
        )
    except (ProjectRegistryError, AccessControlError) as error:
        _exit_with_error(error)
    typer.echo(render_project(project))


@project_app.command("list")
def list_projects(token: str = typer.Option(...)) -> None:
    """List projects visible to the authenticated user."""
    service = create_project_registry_service()
    try:
        projects = service.list_projects(token)
    except (ProjectRegistryError, AccessControlError) as error:
        _exit_with_error(error)
    for project in projects:
        typer.echo(render_project(project))
        typer.echo("")


@project_app.command("show")
def show_project(token: str = typer.Option(...), project_id: int = typer.Option(...)) -> None:
    """Show a specific project visible to the authenticated user."""
    service = create_project_registry_service()
    try:
        project = service.get_project(token, project_id)
    except (ProjectRegistryError, AccessControlError) as error:
        _exit_with_error(error)
    typer.echo(render_project(project))


@project_app.command("configure-lifecycle")
def configure_lifecycle(
    token: str = typer.Option(...),
    project_id: int = typer.Option(...),
    map_status: str | None = typer.Option(default=None),
    map_start: str | None = typer.Option(default=None),
    map_stop: str | None = typer.Option(default=None),
    map_restart: str | None = typer.Option(default=None),
    status_unconfigured: bool = typer.Option(default=False),
    start_unconfigured: bool = typer.Option(default=False),
    stop_unconfigured: bool = typer.Option(default=False),
    restart_unconfigured: bool = typer.Option(default=False),
) -> None:
    """Replace lifecycle function mappings and explicit unconfigured decisions."""
    service = create_project_registry_service()
    mappings = _build_mapping_inputs(map_status, map_start, map_stop, map_restart)
    unconfigured_actions = _build_unconfigured_actions(
        status_unconfigured,
        start_unconfigured,
        stop_unconfigured,
        restart_unconfigured,
    )
    try:
        project = service.update_lifecycle_function_configuration(
            UpdateLifecycleFunctionConfigurationCommand(
                token=token,
                project_id=project_id,
                mappings=mappings,
                unconfigured_actions=unconfigured_actions,
            )
        )
    except (ProjectRegistryError, AccessControlError) as error:
        _exit_with_error(error)
    typer.echo(render_project(project))


@project_app.command("reload")
def reload_project(token: str = typer.Option(...), project_id: int = typer.Option(...)) -> None:
    """Reload lifecycle function detection for one visible project."""
    service = create_project_registry_service()
    try:
        result = service.reload_project(
            ReloadProjectCommand(token=token, project_id=project_id)
        )
    except (ProjectRegistryError, AccessControlError) as error:
        _exit_with_error(error)
    typer.echo(render_project_reload_result(result))


@project_app.command("reload-many")
def reload_projects(
    token: Annotated[str, typer.Option()],
    project_id: Annotated[list[int], typer.Option()],
) -> None:
    """Reload lifecycle function detection for many visible projects in sequence."""
    service = create_project_registry_service()
    try:
        results = service.reload_projects(
            ReloadProjectsCommand(token=token, project_ids=tuple(project_id))
        )
    except (ProjectRegistryError, AccessControlError) as error:
        _exit_with_error(error)
    for result in results:
        typer.echo(render_project_reload_result(result))
        typer.echo("")


@project_app.command("add-owner")
def add_project_owner(
    token: str = typer.Option(...),
    project_id: int = typer.Option(...),
    user_id: int = typer.Option(...),
) -> None:
    """Add a project owner as an authenticated admin."""
    service = create_project_registry_service()
    try:
        project = service.add_project_owner(
            UpdateProjectOwnerCommand(token=token, project_id=project_id, user_id=user_id)
        )
    except (ProjectOwnershipError, ProjectRegistryError, AccessControlError) as error:
        _exit_with_error(error)
    typer.echo(render_project(project))


@project_app.command("remove-owner")
def remove_project_owner(
    token: str = typer.Option(...),
    project_id: int = typer.Option(...),
    user_id: int = typer.Option(...),
) -> None:
    """Remove a project owner as an authenticated admin."""
    service = create_project_registry_service()
    try:
        project = service.remove_project_owner(
            UpdateProjectOwnerCommand(token=token, project_id=project_id, user_id=user_id)
        )
    except (ProjectOwnershipError, ProjectRegistryError, AccessControlError) as error:
        _exit_with_error(error)
    typer.echo(render_project(project))


@lifecycle_app.command("status")
def lifecycle_status(token: str = typer.Option(...), project_id: int = typer.Option(...)) -> None:
    """Execute the status lifecycle action for a project."""
    _execute_lifecycle_action(
        token=token,
        project_id=project_id,
        action=CanonicalLifecycleAction.STATUS,
    )


@lifecycle_app.command("start")
def lifecycle_start(token: str = typer.Option(...), project_id: int = typer.Option(...)) -> None:
    """Execute the start lifecycle action for a project."""
    _execute_lifecycle_action(
        token=token,
        project_id=project_id,
        action=CanonicalLifecycleAction.START,
    )


@lifecycle_app.command("stop")
def lifecycle_stop(token: str = typer.Option(...), project_id: int = typer.Option(...)) -> None:
    """Execute the stop lifecycle action for a project."""
    _execute_lifecycle_action(
        token=token,
        project_id=project_id,
        action=CanonicalLifecycleAction.STOP,
    )


@lifecycle_app.command("restart")
def lifecycle_restart(token: str = typer.Option(...), project_id: int = typer.Option(...)) -> None:
    """Execute the restart lifecycle action for a project."""
    _execute_lifecycle_action(
        token=token,
        project_id=project_id,
        action=CanonicalLifecycleAction.RESTART,
    )


@runtime_app.command("inspect")
def inspect_runtime(token: str = typer.Option(...), project_id: int = typer.Option(...)) -> None:
    """Inspect runtime data for a project visible to the authenticated user."""
    service = create_runtime_inspection_service()
    try:
        snapshot = service.inspect_runtime(
            InspectRuntimeCommand(token=token, project_id=project_id)
        )
    except (ProjectRegistryError, AccessControlError) as error:
        _exit_with_error(error)
    typer.echo(render_runtime_snapshot(snapshot))


@audit_app.command("events")
def audit_events(token: str = typer.Option(...), limit: int = typer.Option(default=25)) -> None:
    """List recent audit events as an authenticated admin."""
    service = create_audit_history_service()
    try:
        events = service.list_recent_events(ListAuditEventsCommand(token=token, limit=limit))
    except (AuditHistoryError, AccessControlError) as error:
        _exit_with_error(error)
    for event in events:
        typer.echo(render_audit_event(event))
        typer.echo("")


def run() -> None:
    """Execute the CLI application."""
    app()
