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
        "docs/plans/review/README.md",
        "docs/decisions/README.md",
        "docs/capabilities/access-control/README.md",
        "docs/reference/external-surfaces.md",
        "docs/guides/user-guide.md",
    ]

    for relative_path in expected_paths:
        assert (ROOT / relative_path).is_file(), relative_path


def test_nonterminal_plans_have_required_delivery_metadata() -> None:
    required_keys = (
        "id:",
        "type:",
        "requires_pull_request:",
        "expected_version_impact:",
        "actual_version_impact:",
        "priority:",
        "sequence:",
        "depends_on:",
        "authorized_capabilities:",
        "validation:",
        "documentation_updates:",
    )

    for status in ("backlog", "active", "review"):
        for plan in (ROOT / "docs/plans" / status).glob("*.md"):
            if plan.name == "README.md":
                continue
            text = plan.read_text(encoding="utf-8")
            assert f"status: {status}" in text
            assert "requires_pull_request: true" in text
            assert re.search(r"^priority: (high|medium|low)$", text, re.MULTILINE)
            for key in required_keys:
                assert key in text, f"{plan.relative_to(ROOT)} missing {key}"


def test_plan_directory_matches_declared_status() -> None:
    for status in ("active", "review", "completed"):
        for plan in (ROOT / "docs/plans" / status).glob("*.md"):
            if plan.name != "README.md":
                assert f"status: {status}" in plan.read_text(encoding="utf-8")


def test_backlog_sequence_and_dependencies_are_consistent() -> None:
    pending_plans = [
        plan
        for status in ("backlog", "active", "review")
        for plan in (ROOT / "docs/plans" / status).glob("*.md")
        if plan.name != "README.md"
    ]
    metadata = {plan: plan.read_text(encoding="utf-8") for plan in pending_plans}
    identifiers = {
        re.search(r"^id: ([^\n]+)$", text, flags=re.MULTILINE).group(1): plan
        for plan, text in metadata.items()
    }
    sequences = {
        plan: int(re.search(r"^sequence: (\d+)$", text, flags=re.MULTILINE).group(1))
        for plan, text in metadata.items()
    }

    assert sorted(sequences.values()) == list(range(1, len(pending_plans) + 1))

    roadmap = (ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    for plan, text in metadata.items():
        plan_id = re.search(r"^id: ([^\n]+)$", text, flags=re.MULTILINE).group(1)
        assert f"| {sequences[plan]} | [{plan_id}:" in roadmap
        dependencies = re.search(
            r"^depends_on:\n((?:  - [^\n]+\n)*)", text, flags=re.MULTILINE
        )
        if dependencies is None:
            continue
        for dependency in re.findall(r"^  - ([^\n]+)$", dependencies.group(1), re.MULTILINE):
            assert dependency in identifiers, f"{plan_id} has unknown dependency {dependency}"
            assert sequences[identifiers[dependency]] < sequences[plan]


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
