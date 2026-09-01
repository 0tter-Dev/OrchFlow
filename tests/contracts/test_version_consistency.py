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
    pyproject = tomllib.loads(_read_text("pyproject.toml"))
    version = pyproject["project"]["version"]
    assert isinstance(version, str)
    return version


def _single_match(pattern: str, text: str, label: str) -> str:
    matches = re.findall(pattern, text)
    assert len(matches) == 1, f"{label} should contain exactly one version match."
    return matches[0]


def test_version_bearing_metadata_files_are_synchronized() -> None:
    version = _project_version()
    package_json = json.loads(_read_text("interface/web/package.json"))
    init_version = _single_match(
        rf'__version__ = "({SEMVER_PATTERN})"',
        _read_text("src/orchflow/__init__.py"),
        "src/orchflow/__init__.py",
    )
    lock_version = _single_match(
        rf'\[\[package\]\]\s+name = "orchflow"\s+version = "({SEMVER_PATTERN})"',
        _read_text("uv.lock"),
        "uv.lock orchflow package block",
    )

    assert package_json["version"] == version
    assert init_version == version
    assert lock_version == version


def test_version_asserting_contract_tests_are_synchronized() -> None:
    version = _project_version()

    api_version = _single_match(
        rf'"version": "({SEMVER_PATTERN})"',
        _read_text("tests/contracts/test_api_smoke.py"),
        "tests/contracts/test_api_smoke.py",
    )
    cli_version = _single_match(
        rf'OrchFlow ({SEMVER_PATTERN})',
        _read_text("tests/contracts/test_cli_smoke.py"),
        "tests/contracts/test_cli_smoke.py",
    )

    assert api_version == version
    assert cli_version == version


def test_current_version_documentation_references_are_synchronized() -> None:
    version = _project_version()
    version_label = f"v{version}"
    version_reference_patterns = {
        "README.md": [
            r"In `(v0\.\d+\.\d+)`",
            r"Out Of Scope For (v0\.\d+\.\d+)",
            r"currently in the `(v0\.\d+\.\d+)` implementation stage",
        ],
        "docs/PROJECT-ARCHITECTURE.md": [
            r"In `(v0\.\d+\.\d+)`",
            r"Non-Goals For (v0\.\d+\.\d+)",
            r"should not, in `(v0\.\d+\.\d+)`",
            r"For `(v0\.\d+\.\d+)`, the selected backend persistence stack",
        ],
        "docs/DEVELOPMENT-GUIDE.md": [
            r"selected for `(v0\.\d+\.\d+)`",
        ],
        "docs/GIT-GITHUB-FLOW.md": [
            r"heavy Git Flow model in `(v0\.\d+\.\d+)`",
            r"frontend package manager for `(v0\.\d+\.\d+)`",
            r"quality baseline needed for `(v0\.\d+\.\d+)`",
        ],
        "docs/STATUS.md": [
            r"currently in the `(v0\.\d+\.\d+)` implementation stage",
            r"operating in `(v0\.\d+\.\d+)`",
        ],
        "docs/TO-DO.md": [
            r"`(v0\.\d+\.\d+)` consolidates",
            r"managed projects in `(v0\.\d+\.\d+)`",
        ],
        "docs/context/ai-agent-adapter.md": [
            r"implemented in `(v0\.\d+\.\d+)`",
        ],
        "docs/context/interface-layer.md": [
            r"operational clarity in `(v0\.\d+\.\d+)`",
        ],
        "docs/context/lifecycle-script-template.md": [
            r"Windows-first for `(v0\.\d+\.\d+)`",
        ],
        "docs/context/project-adapter.md": [
            r"operational authority in `(v0\.\d+\.\d+)`",
        ],
    }

    for relative_path, patterns in version_reference_patterns.items():
        text = _read_text(relative_path)
        for pattern in patterns:
            assert _single_match(pattern, text, f"{relative_path}:{pattern}") == version_label
