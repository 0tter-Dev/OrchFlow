"""Repository contract tests for the documentation information architecture."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_documentation_topology_exists() -> None:
    expected_paths = [
        "docs/START-HERE.md",
        "docs/DOCUMENTATION-GUIDE.md",
        "docs/ROADMAP.md",
        "docs/plans/README.md",
        "docs/decisions/README.md",
        "docs/capabilities/access-control/README.md",
        "docs/reference/external-surfaces.md",
        "docs/guides/user-guide.md",
    ]

    for relative_path in expected_paths:
        assert (ROOT / relative_path).is_file(), relative_path


def test_active_plans_have_required_metadata() -> None:
    required_keys = (
        "id:",
        "status: active",
        "type:",
        "requires_pull_request:",
        "expected_version_impact:",
        "authorized_capabilities:",
        "validation:",
        "documentation_updates:",
    )
    active_plans = list((ROOT / "docs/plans/active").glob("*.md"))

    for plan in active_plans:
        if plan.name == "README.md":
            continue
        text = plan.read_text(encoding="utf-8")
        for key in required_keys:
            assert key in text, f"{plan.relative_to(ROOT)} missing {key}"


def test_internal_markdown_links_resolve() -> None:
    markdown_files = [ROOT / "README.md", ROOT / "AGENTS.md", *ROOT.glob("docs/**/*.md")]
    for document in markdown_files:
        text = document.read_text(encoding="utf-8")
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = link.split("#", maxsplit=1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            assert (document.parent / target).exists(), (
                f"{document.relative_to(ROOT)} has broken link: {link}"
            )
