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
- Keep infrastructure dependencies outside the core business layer
- Avoid leaking persistence or transport details into domain rules
- Favor explicit contracts and use cases over ad hoc service coupling

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

## Technology Decision Policy

The initial documentation intentionally avoids locking the full stack too early.

Technology choices should be made according to:

- fit for the documented architecture
- support for local-first workflows
- testability
- maintainability
- operational clarity

`SQLite` is currently the leading persistence direction, but the broader stack remains open for deliberate selection later.
