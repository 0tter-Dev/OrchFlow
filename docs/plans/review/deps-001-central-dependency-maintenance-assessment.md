---
id: deps-001
status: review
type: docs
requires_pull_request: true
expected_version_impact: none
actual_version_impact: pending
priority: medium
sequence: 7
depends_on: []
authorized_capabilities: []
decision_records:
  - docs/decisions/ADR-0005-central-dependency-maintenance-sequencing.md
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

User approval was recorded on `2026-09-13`. The assessment retained the current resolved baseline: `uv lock --dry-run` resolved 98 packages with no lockfile changes; backend lint and type checks passed; and the complete backend suite passed (152 tests) with isolated Windows temporary directories. The evidence-backed sequencing decision is recorded in [ADR-0005](../../decisions/ADR-0005-central-dependency-maintenance-sequencing.md).

The assessment recommends no immediate central dependency upgrade and no release version change. FastAPI, Starlette, Pydantic, SQLAlchemy, Alembic, bcrypt, cryptography, JWT-related dependencies, and backend tooling remain on their resolved stable lines. LiteLLM is explicitly deferred because its rapid release and packaging cadence require a dedicated adapter-boundary compatibility plan. The existing focused backlog plans remain the approved follow-up path for pnpm 12 (`deps-002`), Node.js and Corepack (`deps-003`), Vite (`web-013`), and ESLint (`web-014`); each must obtain its own explicit approval before implementation. Delivered in commit `dd08abb` through [PR #71](https://github.com/0tter-Dev/OrchFlow/pull/71), awaiting review and merge.
