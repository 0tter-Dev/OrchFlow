"""Repository contract tests for release automation helpers."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _release_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("release_script", ROOT / "scripts" / "release.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_release_tag_must_match_project_version() -> None:
    release = _release_module()

    release.validate_release_tag("v0.3.18", "0.3.18")


def test_release_tag_rejects_mismatched_or_unprefixed_versions() -> None:
    release = _release_module()

    with pytest.raises(ValueError, match="does not match"):
        release.validate_release_tag("v0.3.19", "0.3.18")

    with pytest.raises(ValueError, match="v0.x.y"):
        release.validate_release_tag("0.3.18", "0.3.18")


def test_release_notes_group_conventional_commit_subjects() -> None:
    release = _release_module()
    entries = [
        release.CommitEntry(short_hash="abc1234", subject="feat(api): add release route"),
        release.CommitEntry(short_hash="def5678", subject="fix(cli): reject invalid token"),
        release.CommitEntry(short_hash="123abcd", subject="docs(devops): document release flow"),
        release.CommitEntry(short_hash="456def0", subject="manual merge commit"),
    ]

    notes = release.release_notes_markdown(
        tag="v0.3.18",
        version="0.3.18",
        revision_range="v0.3.0..HEAD",
        entries=entries,
    )

    assert "# v0.3.18" in notes
    assert "Revision range: `v0.3.0..HEAD`" in notes
    assert "## Features" in notes
    assert "- feat(api): add release route (abc1234)" in notes
    assert "## Fixes" in notes
    assert "- fix(cli): reject invalid token (def5678)" in notes
    assert "## Documentation" in notes
    assert "- docs(devops): document release flow (123abcd)" in notes
    assert "## Other Changes" in notes
    assert "- manual merge commit (456def0)" in notes
