"""Tests for the ideal lifecycle function model."""

from __future__ import annotations

from orchflow.domain.lifecycle_function_model import (
    IDEAL_LIFECYCLE_FUNCTION_BY_ACTION,
    IDEAL_LIFECYCLE_FUNCTIONS,
    LifecycleFunctionConfigurationState,
    ProjectConfigurationHealth,
    build_lifecycle_function_configurations,
    derive_project_configuration_health,
)
from orchflow.domain.project_registry import CanonicalLifecycleAction


def test_ideal_lifecycle_functions_cover_expected_actions_in_order() -> None:
    assert tuple(function.action for function in IDEAL_LIFECYCLE_FUNCTIONS) == (
        CanonicalLifecycleAction.STATUS,
        CanonicalLifecycleAction.START,
        CanonicalLifecycleAction.STOP,
        CanonicalLifecycleAction.RESTART,
    )


def test_ideal_lifecycle_functions_define_descriptions_and_preferred_identifiers() -> None:
    expected_identifiers = {
        CanonicalLifecycleAction.STATUS: "STATUS",
        CanonicalLifecycleAction.START: "START",
        CanonicalLifecycleAction.STOP: "STOP",
        CanonicalLifecycleAction.RESTART: "RESTART",
    }

    for function in IDEAL_LIFECYCLE_FUNCTIONS:
        assert function.description
        assert function.preferred_script_identifier == expected_identifiers[function.action]
        assert IDEAL_LIFECYCLE_FUNCTION_BY_ACTION[function.action] == function


def test_lifecycle_function_configuration_states_match_documented_contract() -> None:
    assert tuple(LifecycleFunctionConfigurationState) == (
        LifecycleFunctionConfigurationState.CONFIGURED,
        LifecycleFunctionConfigurationState.UNDEFINED,
        LifecycleFunctionConfigurationState.UNCONFIGURED,
    )
    assert LifecycleFunctionConfigurationState.CONFIGURED.value == "configured"
    assert LifecycleFunctionConfigurationState.UNDEFINED.value == "undefined"
    assert LifecycleFunctionConfigurationState.UNCONFIGURED.value == "unconfigured"


def test_project_configuration_health_is_derived_from_function_states() -> None:
    complete_configuration = build_lifecycle_function_configurations(
        {
            CanonicalLifecycleAction.STATUS: "STATUS",
            CanonicalLifecycleAction.START: "START",
            CanonicalLifecycleAction.STOP: "STOP",
            CanonicalLifecycleAction.RESTART: "RESTART",
        }
    )
    partial_configuration = build_lifecycle_function_configurations(
        {CanonicalLifecycleAction.STATUS: "STATUS"}
    )
    blocked_configuration = build_lifecycle_function_configurations({})

    assert derive_project_configuration_health(complete_configuration) is (
        ProjectConfigurationHealth.COMPLETE
    )
    assert derive_project_configuration_health(partial_configuration) is (
        ProjectConfigurationHealth.PARTIAL
    )
    assert derive_project_configuration_health(blocked_configuration) is (
        ProjectConfigurationHealth.BLOCKED
    )
