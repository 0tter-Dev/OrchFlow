# Development Guide

## Purpose

This guide defines how OrchFlow should be developed, changed, and maintained.

## Development Priorities

1. Preserve product scope and clarity
2. Keep business rules centralized
3. Prefer explicit operational contracts
4. Keep documentation and implementation synchronized
5. Optimize for maintainability before convenience

## Architectural Rules

- Follow clean architecture or an equivalent layered model
- Keep domain and application rules independent from CLI, API, and UI delivery concerns
- Keep project-specific execution behavior behind explicit adapter contracts
- Keep infrastructure dependencies outside the core business layer
- Avoid leaking persistence or transport details into domain rules
- Avoid leaking environment-loading concerns into domain rules
- Favor explicit contracts and use cases over ad hoc service coupling
- Keep interface clients separated from the backend core through the API boundary

## Code Quality Rules

- Apply SOLID principles pragmatically
- Prefer cohesive modules with clear responsibilities
- Avoid dead code, commented-out code, and speculative abstractions
- Avoid tightly coupling business logic to framework-specific behavior
- Keep side effects explicit and testable
- Favor readability over cleverness

## Scope Control

Changes are acceptable when they:

- strengthen the documented architecture
- improve maintainability without changing project intent
- clarify lifecycle control behavior
- improve security, validation, or testability

Changes require explicit review when they:

- alter the lifecycle contract away from `.bat` as the operational authority
- weaken access control rules
- introduce remote-first behavior
- add container orchestration as a first-class concern
- replace human-reviewed configuration with autonomous AI decisions
- couple the core directly to a single AI provider instead of using an adapter boundary
- materially reshape the project structure or strategic dependencies

## Documentation Rules

- New features must be reflected in `docs/STATUS.md`
- Feature behavior belongs in the relevant file under `docs/context/`
- Scope or policy changes belong in `docs/PROJECT-ARCHITECTURE.md`
- Cross-feature relationship changes belong in `docs/INDEX.md`
- User-facing workflow changes should be reflected in `docs/USER-GUIDE.md`

## Naming Rules

- prefer kebab-case for new documentation files, non-Python source-adjacent files, branch names, and free-form repository artifact names
- avoid spaces in file and directory names
- use underscores only when a language, framework, platform, or external tool requires an exact name
- keep standardized dotfiles and externally required repository names unchanged

Examples of valid required exceptions:

- `.github/ISSUE_TEMPLATE/`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/ISSUE_TEMPLATE/config.yml`
- Python dunder files such as `__init__.py`
- Git-standard files such as `.gitignore`

## Configuration Rules

- Runtime configuration should be loaded from environment variables
- A versioned `.env.example` should document the expected local variables
- Local secrets must stay out of version control
- Configuration validation should happen near the application boundary

## Testing Direction

The project should adopt tests progressively in the following order:

1. domain and application behavior
2. adapter contract tests for CLI and API
3. infrastructure integration tests where practical
4. interface-level tests for critical user flows

## Git And GitHub Direction

- Use Git as the source of truth for version history
- Keep changes small and reviewable
- Prefer short-lived branches
- Require pull-request review for protected branches
- Use semantic versioning
- Treat documentation and tests as part of the expected change set

## CI/CD Direction

At minimum, the project should prepare for:

- formatting or style validation
- static analysis or linting
- automated tests
- build verification
- release tagging and changelog discipline

Deployment automation may be added later, but CI quality gates should be designed early.

## Selected Technology Baseline

The current implementation baseline is:

- backend language: `Python`
- package and environment management: `uv`
- CLI: `Typer`
- API: `FastAPI`
- persistence: `SQLite`
- ORM and migrations: `SQLAlchemy` and `Alembic`
- authentication: JWT and `bcrypt`
- backend tests: `pytest`
- quality tooling: `ruff` and `mypy`
- initial web interface layer: `React`, `TypeScript`, and `Vite`

## Technology Decision Policy

The core technology direction is now selected for `v0.1.0`.

Future changes should still be evaluated according to:

- fit for the documented architecture
- support for local-first workflows
- testability
- maintainability
- operational clarity
