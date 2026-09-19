"""Contract checks for the versioned local configuration inventory."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from orchflow.infrastructure.config.contract import (
    CONFIGURATION_CONTRACT,
    redact_configuration_value,
)
from orchflow.infrastructure.config.settings import AppSettings

ROOT = Path(__file__).resolve().parents[2]


def _example_keys(path: Path) -> set[str]:
    return {
        line.partition("=")[0]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }


def test_environment_examples_are_covered_by_the_configuration_contract() -> None:
    contract_names = {variable.name for variable in CONFIGURATION_CONTRACT}

    assert _example_keys(ROOT / ".env.example") <= contract_names
    assert _example_keys(ROOT / "interface" / "web" / ".env.example") <= contract_names


def test_contract_has_one_entry_for_each_supported_variable() -> None:
    names = [variable.name for variable in CONFIGURATION_CONTRACT]

    assert len(names) == len(set(names))
    assert all(variable.classification != "deprecated" for variable in CONFIGURATION_CONTRACT)
    assert all(variable.value_format for variable in CONFIGURATION_CONTRACT)
    assert all(variable.consumer for variable in CONFIGURATION_CONTRACT)


def test_sensitive_configuration_values_are_redacted() -> None:
    assert redact_configuration_value("ORCHFLOW_JWT_SECRET", "local-secret") == "[redacted]"
    assert redact_configuration_value("ORCHFLOW_LITELLM_API_KEY", "provider-secret") == "[redacted]"
    assert redact_configuration_value("ORCHFLOW_LITELLM_API_KEY", "") == "[not configured]"
    assert redact_configuration_value("ORCHFLOW_API_HOST", "localhost") == "localhost"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("api_port", "not-a-port"),
        ("api_port", 0),
        ("jwt_access_token_expire_minutes", "not-a-number"),
        ("jwt_access_token_expire_minutes", 0),
    ],
)
def test_invalid_typed_critical_settings_fail_at_the_boundary(field: str, value: str) -> None:
    with pytest.raises(ValidationError):
        AppSettings.model_validate({field: value})
