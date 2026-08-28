"""Ideal lifecycle function model for managed projects."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from orchflow.domain.project_registry import CanonicalLifecycleAction


class LifecycleFunctionConfigurationState(StrEnum):
    """Configuration state for one ideal lifecycle function."""

    CONFIGURED = "configured"
    UNDEFINED = "undefined"
    UNCONFIGURED = "unconfigured"


@dataclass(frozen=True, slots=True)
class IdealLifecycleFunction:
    """Reference definition for one expected project lifecycle function."""

    action: CanonicalLifecycleAction
    description: str
    preferred_script_identifier: str


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
