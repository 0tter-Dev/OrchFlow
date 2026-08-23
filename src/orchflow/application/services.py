"""Application service factory helpers."""

from orchflow.application.access_control import AccessControlService
from orchflow.application.bootstrap import BootstrapStatusService
from orchflow.application.lifecycle import LifecycleOrchestrationService
from orchflow.application.project_registry import ProjectRegistryService
from orchflow.application.runtime_inspection import RuntimeInspectionService
from orchflow.infrastructure.config.settings import AppSettings, get_settings
from orchflow.infrastructure.persistence.project_registry_repository import (
    SqlAlchemyProjectRegistryRepository,
)
from orchflow.infrastructure.persistence.repositories import SqlAlchemyUserRepository
from orchflow.infrastructure.persistence.session import (
    create_session_factory,
    initialize_database,
)
from orchflow.infrastructure.project_adapter.batch_adapter import WindowsBatchProjectAdapter
from orchflow.infrastructure.runtime_inspection.windows import WindowsRuntimeInspector
from orchflow.infrastructure.security.auth import BcryptPasswordHasher, JwtTokenManager


def create_bootstrap_service(settings: AppSettings | None = None) -> BootstrapStatusService:
    """Create the bootstrap service with the current settings."""
    return BootstrapStatusService(settings=settings or get_settings())


def create_access_control_service(settings: AppSettings | None = None) -> AccessControlService:
    """Create the access control application service."""
    current_settings = settings or get_settings()
    initialize_database(current_settings)
    session_factory = create_session_factory(current_settings)
    repository = SqlAlchemyUserRepository(session_factory)
    password_hasher = BcryptPasswordHasher()
    token_manager = JwtTokenManager(current_settings)
    return AccessControlService(repository, password_hasher, token_manager)


def create_project_registry_service(
    settings: AppSettings | None = None,
) -> ProjectRegistryService:
    """Create the project registry application service."""
    current_settings = settings or get_settings()
    initialize_database(current_settings)
    session_factory = create_session_factory(current_settings)
    repository = SqlAlchemyProjectRegistryRepository(session_factory)
    access_control_service = create_access_control_service(current_settings)
    return ProjectRegistryService(repository, access_control_service)


def create_lifecycle_orchestration_service(
    settings: AppSettings | None = None,
) -> LifecycleOrchestrationService:
    """Create the lifecycle orchestration application service."""
    current_settings = settings or get_settings()
    initialize_database(current_settings)
    session_factory = create_session_factory(current_settings)
    repository = SqlAlchemyProjectRegistryRepository(session_factory)
    access_control_service = create_access_control_service(current_settings)
    project_registry_service = ProjectRegistryService(repository, access_control_service)
    adapter = WindowsBatchProjectAdapter()
    runtime_inspector = WindowsRuntimeInspector()
    return LifecycleOrchestrationService(
        project_registry_service=project_registry_service,
        current_user_resolver=access_control_service,
        adapter=adapter,
        audit_recorder=repository,
        runtime_inspector=runtime_inspector,
    )


def create_runtime_inspection_service(
    settings: AppSettings | None = None,
) -> RuntimeInspectionService:
    """Create the runtime inspection application service."""
    current_settings = settings or get_settings()
    initialize_database(current_settings)
    session_factory = create_session_factory(current_settings)
    repository = SqlAlchemyProjectRegistryRepository(session_factory)
    access_control_service = create_access_control_service(current_settings)
    project_registry_service = ProjectRegistryService(repository, access_control_service)
    inspector = WindowsRuntimeInspector()
    return RuntimeInspectionService(
        project_registry_service=project_registry_service,
        current_user_resolver=access_control_service,
        inspector=inspector,
    )
