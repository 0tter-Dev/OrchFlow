# ADR-0005: Central Dependency Maintenance Sequencing

## Context

OrchFlow's central dependencies cross public API, CLI, persistence, authentication, the optional AI boundary, and Windows contributor tooling. An indiscriminate lockfile refresh would make a regression hard to attribute and could silently change a supported contract.

The `deps-001` assessment on `2026-09-13` resolved 98 packages without lockfile changes. The resolved baseline already includes FastAPI 0.141.1, Starlette 1.6.0, Pydantic 2.13.4, SQLAlchemy 2.0.52, Alembic 1.19.1, Typer 0.27.1, Click 8.4.2, LiteLLM 1.98.0, bcrypt 5.0.0, cryptography 50.0.0, uv 0.12.5, Ruff 0.16.4, mypy 2.3.1, and pytest 9.1.1.

## Decision

Keep the resolved baseline and do not perform a central dependency upgrade in `deps-001`.

Treat central maintenance as compatibility work grouped by integration boundary:

- defer LiteLLM changes until a dedicated AI-boundary compatibility plan can exercise the adapter, manifest, proposal, review, and application contracts;
- keep FastAPI, Starlette, Pydantic, SQLAlchemy, Alembic, and authentication/cryptography packages on their resolved stable lines unless a concrete security advisory or supported release requires a focused plan;
- keep the pnpm, Node.js, Corepack, Vite, and ESLint follow-ups separated in the existing `deps-002`, `deps-003`, `web-013`, and `web-014` plans;
- require release-note review, dry-run resolution, and the affected validation surface before any selected package group changes.

## Consequences

The current lockfile remains reproducible and every later upgrade has a narrow regression surface. This intentionally delays available upstream releases where their compatibility, packaging, or behavioral impact has not been demonstrated against OrchFlow's local-first contracts.

FastAPI's resolved 0.141.1 line is current in its release notes. SQLAlchemy 2.1 has documented migration behavior and is therefore not a patch-level refresh. Typer 0.27 introduced breaking changes before the currently resolved 0.27.1, and LiteLLM's rapid release cadence and packaging distinctions require adapter-level validation rather than an unreviewed uplift. The security-related resolved packages are left unchanged because this assessment found no repository-specific evidence requiring an immediate migration.

## Alternatives Considered

Running a blanket `uv lock --upgrade` was rejected because it would combine API, CLI, persistence, authentication, AI, and tooling risk in one unreviewable change. Updating only the most visible package was also rejected because transitive constraints could still change central behavior without complete regression coverage.

## Canonical Links

[Central Dependency Maintenance Assessment](../plans/review/deps-001-central-dependency-maintenance-assessment.md), [Git And GitHub Flow](../guides/git-and-github-flow.md), [FastAPI release notes](https://fastapi.tiangolo.com/release-notes/), [SQLAlchemy 2.1 migration notes](https://docs.sqlalchemy.org/en/21/changelog/migration_21.html), [Typer release notes](https://typer.tiangolo.com/release-notes/), [uv versioning policy](https://docs.astral.sh/uv/reference/policies/versioning/), and [LiteLLM releases](https://github.com/BerriAI/litellm/releases).
