---
id: deps-001
status: backlog
type: docs
requires_pull_request: true
expected_version_impact: none
authorized_capabilities: []
decision_records: []
validation:
  - dependency-resolution-dry-run
  - backend-validation
  - documentation-structure-test
documentation_updates:
  - docs/ROADMAP.md
  - docs/STATUS.md
---

# Central Dependency Maintenance Assessment

## Objective

Create an evidence-backed, compatibility-first decision record for deferred central dependency updates.

## Context

Core updates have value but carry higher risk across public API, CLI, migrations, authentication, and AI boundaries. They must not be bundled with the web experience work.

## Decisions

Assess each candidate independently, then create a focused implementation plan only for approved upgrades: LiteLLM; Typer and Click; FastAPI, Starlette, Pydantic, and pydantic-core; SQLAlchemy and Alembic; cryptography, bcrypt, and JWT-related packages; and `uv`, Ruff, mypy, pytest, and related tooling.

## Scope

Review release notes, dependency constraints, dry-run resolution, affected contracts, and required regression coverage. Record recommended sequencing and explicit reasons to defer any candidate.

## Out Of Scope

Installing or upgrading central dependencies, changing public contracts, or reading capabilities without explicit approval.

## Acceptance Criteria

Every candidate has a risk classification, affected validation surface, proposed version decision, and a separate next plan or documented deferral.

## Validation

Run dry-run dependency resolution, the relevant existing validation baseline, and documentation checks without changing dependency versions.

## Documentation Updates

Update the Roadmap, status, and any resulting focused backlog plans.

## Outcome

Backlog candidate; not started.
