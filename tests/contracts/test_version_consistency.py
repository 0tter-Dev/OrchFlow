"""Repository contract tests for version bump discipline."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEMVER_PATTERN = r"0\.\d+\.\d+"


def _read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _project_version() -> str:
    value = tomllib.loads(_read_text("pyproject.toml"))["project"]["version"]
    assert isinstance(value, str)
    return value


def _single_match(pattern: str, text: str, label: str) -> str:
    matches = re.findall(pattern, text)
    assert len(matches) == 1, f"{label} should contain exactly one version match."
    return matches[0]


def test_version_bearing_metadata_files_are_synchronized() -> None:
    version = _project_version()
    assert json.loads(_read_text("interface/web/package.json"))["version"] == version
    package_version = _single_match(
        rf'__version__ = "({SEMVER_PATTERN})"',
        _read_text("src/orchflow/__init__.py"),
        "package",
    )
    lock_version = _single_match(
        rf'\[\[package\]\]\s+name = "orchflow"\s+version = "({SEMVER_PATTERN})"',
        _read_text("uv.lock"),
        "lock",
    )
    assert package_version == version
    assert lock_version == version


def test_version_asserting_contract_tests_are_synchronized() -> None:
    version = _project_version()
    api_version = _single_match(
        rf'"version": "({SEMVER_PATTERN})",',
        _read_text("tests/contracts/test_api_smoke.py"),
        "api",
    )
    cli_version = _single_match(
        rf'OrchFlow ({SEMVER_PATTERN})',
        _read_text("tests/contracts/test_cli_smoke.py"),
        "cli",
    )
    assert api_version == version
    assert cli_version == version


def test_current_version_documentation_references_are_synchronized() -> None:
    version_label = f"v{_project_version()}"
    expected = {
        "README.md": r"Out of scope in `(v0\.\d+\.\d+)`",
        "docs/PROJECT-ARCHITECTURE.md": r"In `(v0\.\d+\.\d+)`",
        "docs/DEVELOPMENT-GUIDE.md": r"selected for `(v0\.\d+\.\d+)`",
        "docs/guides/git-and-github-flow.md": r"heavy Git Flow model in `(v0\.\d+\.\d+)`",
        "docs/STATUS.md": r"in the `(v0\.\d+\.\d+)` implementation stage",
        "docs/capabilities/ai-assistance/README.md": r"implemented in `(v0\.\d+\.\d+)`",
        "docs/capabilities/web-operator-workspace/README.md": (
            r"operational clarity in `(v0\.\d+\.\d+)`"
        ),
        "docs/capabilities/lifecycle-management/script-contract.md": (
            r"Windows-first for `(v0\.\d+\.\d+)`"
        ),
        "docs/capabilities/lifecycle-management/adapter-contract.md": (
            r"operational authority in `(v0\.\d+\.\d+)`"
        ),
    }

    for relative_path, pattern in expected.items():
        assert _single_match(pattern, _read_text(relative_path), relative_path) == version_label
