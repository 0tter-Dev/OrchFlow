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
- Keep lifecycle function matching and configuration-state evaluation in application/domain code, not only in UI warnings
- Keep AI/model connectivity behind the OrchFlow AI assistance adapter; do not call `LiteLLM` directly from domain rules, CLI, API, UI, or unrelated application services
- Keep infrastructure dependencies outside the core business layer
- Avoid leaking persistence or transport details into domain rules
- Avoid leaking environment-loading concerns into domain rules
- Favor explicit contracts and use cases over ad hoc service coupling
- Keep interface clients separated from the backend core through the API boundary

## Code Quality Rules

- Apply SOLID principles pragmatically
- Prefer cohesive modules with clear responsibilities
- Avoid dead code, commented-out code, and speculative abstractions
- Avoid placeholder shared layers or generic kernels unless they have a clear present responsibility
- Avoid tightly coupling business logic to framework-specific behavior
- Keep side effects explicit and testable
- Favor readability over cleverness

## Scope Control

Changes are acceptable when they:

- strengthen the documented architecture
- improve maintainability without changing project intent
- clarify lifecycle control behavior
- improve lifecycle function detection, reload, mapping validation, or operator guidance without weakening the `.bat` contract
- improve security, validation, or testability

Changes require explicit review when they:

- alter the lifecycle contract away from `.bat` as the operational authority
- weaken access control rules
- introduce remote-first behavior
- add container orchestration as a first-class concern
- replace human-reviewed configuration with autonomous AI decisions
- couple the core directly to a single AI provider instead of using an adapter boundary
- bypass the LiteLLM gateway and OrchFlow adapter boundary when implementing AI-assisted behavior
- materially reshape the project structure or strategic dependencies

Future-oriented extensibility is acceptable when it does not add speculative implementation weight, but the project should not pre-build container support or shared-kernel abstractions without a concrete validated need.

## Documentation Rules

- New features must be reflected in `docs/STATUS.md`
- Feature behavior belongs in the relevant file under `docs/context/`
- Scope or policy changes belong in `docs/PROJECT-ARCHITECTURE.md`
- Cross-feature relationship changes belong in `docs/INDEX.md`
- User-facing workflow changes should be reflected in `docs/USER-GUIDE.md`
- Relevant documentation should be updated alongside meaningful implementation changes, especially code changes
- Pull requests must include a semantic version decision and must update all version-bearing files when the change requires a version bump
- `docs/TO-DO.md` should remain focused on the next planned steps and should not retain work that is already implemented
- Changes to established foundations such as the selected stack, business rules, scope boundaries, or non-goals require explicit user approval before they are applied

For AI agents, root-level documentation under `docs/` is the required baseline before any alteration. AI agents must not consult `docs/context/` by default; they may read or update context documents only when the requesting user explicitly authorizes that scope.

After any relevant code change, AI agents must re-evaluate the related documentation and update the documents affected by the change. If a context document appears relevant but has not been authorized, the agent must ask for authorization before consulting it.

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
- Allow both human-driven and agent-driven pull request authorship as long as the documented review and identity rules are respected
- Use semantic versioning
- Treat documentation and tests as part of the expected change set

When an AI agent is allowed to execute Git operations for this repository, it should do so only through the documented repository workflow, using `git` and `gh` through the CLI, a repository-specific Git identity, and leaving review and merge authority to a human maintainer.

For code-changing agent work, the expected delivery path is: implement the focused change, update the relevant documentation, run the relevant backend and/or frontend validations, inspect the diff, create a specific short-lived branch, commit, push, and open a pull request into `main`.

Pull request descriptions should use `.github/PULL_REQUEST_TEMPLATE.md` as the standard repository template. Contributors and AI agents should fill that structure when creating PRs, including the summary, decision notes, validation checklist, documentation checklist, and review notes that apply to the change.

Every pull request should explicitly state the version bump decision. If the change updates behavior, dependencies, public contracts, operational workflow, or documentation-defined scope, the project version should be advanced according to semantic versioning and kept synchronized across package metadata, runtime version reporting, tests, lockfiles, README, status documentation, and any other version-bearing documentation. If no version bump is made, the pull request should explain why.

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
- frontend package manager: `pnpm`
- initial web interface layer: `React`, `TypeScript`, and `Vite`
- AI/model gateway: `LiteLLM`, isolated behind the OrchFlow AI assistance adapter

## Technology Decision Policy

The core technology direction is now selected for `v0.2.15`.

Future changes should still be evaluated according to:

- fit for the documented architecture
- support for local-first workflows
- testability
- maintainability
- operational clarity
