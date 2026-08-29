"""Ideal lifecycle function model for managed projects."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum

from orchflow.domain.project_registry import CanonicalLifecycleAction


class LifecycleFunctionConfigurationState(StrEnum):
    """Configuration state for one ideal lifecycle function."""

    CONFIGURED = "configured"
    UNDEFINED = "undefined"
    UNCONFIGURED = "unconfigured"


class ProjectConfigurationHealth(StrEnum):
    """Derived lifecycle configuration health for one project."""

    COMPLETE = "complete"
    PARTIAL = "partial"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class IdealLifecycleFunction:
    """Reference definition for one expected project lifecycle function."""

    action: CanonicalLifecycleAction
    description: str
    preferred_script_identifier: str


@dataclass(frozen=True, slots=True)
class LifecycleFunctionConfiguration:
    """Project-specific configuration state for one ideal lifecycle function."""

    action: CanonicalLifecycleAction
    description: str
    preferred_script_identifier: str
    state: LifecycleFunctionConfigurationState
    script_label: str | None


IDEAL_LIFECYCLE_FUNCTIONS: tuple[IdealLifecycleFunction, ...] = (
    IdealLifecycleFunction(
        action=CanonicalLifecycleAction.STATUS,
        description=(
            "Report whether the project appears to be running and expose useful "
            "local runtime hints."
        ),
        preferred_script_identifier="STATUS",
    ),
    IdealLifecycleFunction(
        action=CanonicalLifecycleAction.START,
        description=(
            "Start the project through its configured local command and working "
            "directory."
        ),
        preferred_script_identifier="START",
    ),
    IdealLifecycleFunction(
        action=CanonicalLifecycleAction.STOP,
        description=(
            "Stop the project through a clear local process, command, or "
            "port-based strategy."
        ),
        preferred_script_identifier="STOP",
    ),
    IdealLifecycleFunction(
        action=CanonicalLifecycleAction.RESTART,
        description=(
            "Restart the project by applying the stop and start lifecycle flow in "
            "a predictable way."
        ),
        preferred_script_identifier="RESTART",
    ),
)

IDEAL_LIFECYCLE_FUNCTION_BY_ACTION: dict[
    CanonicalLifecycleAction,
    IdealLifecycleFunction,
] = {function.action: function for function in IDEAL_LIFECYCLE_FUNCTIONS}


def build_lifecycle_function_configurations(
    configured_script_labels: Mapping[CanonicalLifecycleAction, str],
    unconfigured_actions: Iterable[CanonicalLifecycleAction] = (),
) -> tuple[LifecycleFunctionConfiguration, ...]:
    """Build function-level configuration state from configured mappings."""
    unconfigured_action_set = set(unconfigured_actions)
    configurations: list[LifecycleFunctionConfiguration] = []
    for function in IDEAL_LIFECYCLE_FUNCTIONS:
        script_label = configured_script_labels.get(function.action)
        if script_label is not None:
            state = LifecycleFunctionConfigurationState.CONFIGURED
        elif function.action in unconfigured_action_set:
            state = LifecycleFunctionConfigurationState.UNCONFIGURED
        else:
            state = LifecycleFunctionConfigurationState.UNDEFINED
        configurations.append(
            LifecycleFunctionConfiguration(
                action=function.action,
                description=function.description,
                preferred_script_identifier=function.preferred_script_identifier,
                state=state,
                script_label=script_label,
            )
        )
    return tuple(configurations)


def derive_project_configuration_health(
    configurations: tuple[LifecycleFunctionConfiguration, ...],
) -> ProjectConfigurationHealth:
    """Derive project-level lifecycle configuration health."""
    configured_count = sum(
        1
        for configuration in configurations
        if configuration.state is LifecycleFunctionConfigurationState.CONFIGURED
    )
    if configured_count == len(configurations):
        return ProjectConfigurationHealth.COMPLETE
    if configured_count > 0:
        return ProjectConfigurationHealth.PARTIAL
    return ProjectConfigurationHealth.BLOCKED
