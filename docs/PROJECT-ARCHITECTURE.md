# Project Architecture

## Purpose

OrchFlow is a local-first project lifecycle orchestrator for software projects. Its goal is to provide a unified way to register projects, control their lifecycle, inspect runtime state, and expose this control through multiple delivery channels without duplicating business rules.

## Product Vision

OrchFlow should help a user manage local development projects with less friction by standardizing how projects are started, stopped, restarted, inspected, and reviewed.

The platform must centralize:

- project registration
- lifecycle control
- runtime inspection
- environment and local configuration management
- user permissions
- operational history
- external access through CLI, API, and interface layers

## Core Principle

In `v0.2.0`, every managed project must have a concrete lifecycle control definition based on a Windows `.bat` script. This script is the authoritative operational contract used by OrchFlow to control the project lifecycle.

The `AI Agent Adapter` is optional and assistive. It may connect OrchFlow to a local AI provider, initially expected to support local `Ollama`, so a user can analyze a selected folder and generate or refine a `.bat` lifecycle script. It must not replace the explicit script contract.

## Goals

- Provide a standardized local orchestration workflow for multiple projects
- Support registration of user-owned projects with explicit lifecycle control definitions
- Offer lifecycle operations such as status, start, stop, and restart
- Expose runtime data such as ports, process identifiers, uptime, CPU, and memory
- Support both command-line and programmatic access through mirrored external interfaces
- Provide a simple visual interface for fast inspection and lifecycle control
- Enforce authentication and authorization through application users and permissions
- Establish a disciplined engineering foundation for Git, GitHub, testing, and CI

## Non-Goals For v0.2.0

- Container orchestration
- Multi-host orchestration
- Automatic download or installation of AI models
- Direct autonomous AI control over project lifecycle actions
- Replacing explicit lifecycle scripts with AI-managed automation
- Full observability platform capabilities
- Distributed agents acting without user supervision

These non-goals should not be treated as a reason to hard-couple the codebase against future evolution, but OrchFlow should not introduce container-oriented behavior or architecture detail unless a later product decision explicitly requires it.

## Primary Actors

- `member`: a regular user who can manage projects according to assigned permissions
- `admin`: a privileged user with full platform access, including user visibility and permission management

## Business Rules

### Project Ownership

- Each project must have a user-facing reference name
- Each project must be associated with one or more authorized users
- Ownership and permission rules must be enforced consistently across CLI, API, and interface channels

### Lifecycle Control

- OrchFlow must support at least `status`, `start`, `stop`, and `restart`
- Lifecycle actions must be routed through a normalized project definition
- lifecycle execution must pass through a generic `Project Adapter` boundary
- OrchFlow should use canonical lifecycle actions internally even when projects expose different script labels
- project-specific action mappings must be persistable, reviewable, and auditable
- Lifecycle operations must be auditable
- Runtime inspection must not be implemented as a UI-only concern

### AI Agent Assistance

- AI analysis is optional
- OrchFlow must mediate all AI interactions through an `AI Agent Adapter`
- the initial provider direction may include local `Ollama`, but the architecture must remain provider-agnostic
- AI assistance must operate only against resources already available and authorized on the machine
- OrchFlow may start a local provider process if needed
- OrchFlow must not download new models automatically
- the user must explicitly authorize project inspection before AI analysis starts
- the user must explicitly authorize creation or overwrite of a lifecycle `.bat` file
- the user must explicitly authorize persistence of AI-suggested action mappings
- AI suggestions and generated files must be reviewable by the user before becoming part of a project definition

### Configuration And Environment

- OrchFlow should use environment-based configuration for local runtime settings
- local configuration must be represented through a documented `.env` contract
- secrets must not be hardcoded in source files
- environment configuration must stay outside core business rules
- default configuration should be development-friendly without weakening security boundaries

### Documentation Governance

- Documentation is part of the product definition, not an afterthought
- Scope changes should be reflected in the Project Architecture and Development Guide
- Feature-level evolution should be tracked in context documents and status documentation

## Functional Boundaries

OrchFlow should:

- register projects
- validate lifecycle definitions
- run lifecycle actions
- inspect runtime state
- load and validate environment configuration
- persist relevant metadata and operational history
- authenticate users
- authorize access to projects and actions
- mediate optional AI-assisted project analysis and script generation
- expose consistent operational capabilities through CLI, API, and interface adapters

OrchFlow should not, in `v0.2.0`:

- behave as a container orchestrator
- assume remote infrastructure control
- infer production-grade deployment logic from local project folders
- treat AI inference as authoritative runtime control

The implementation should avoid speculative abstractions for possible future container support. If that support is ever considered later, it should be introduced through an explicit product decision rather than preemptive design.

## Initial Domain Concepts

- `User`
- `Permission`
- `Project`
- `Project Adapter`
- `Project Lifecycle Script`
- `Lifecycle Action Mapping`
- `Lifecycle Script Template`
- `Project Definition`
- `Runtime Snapshot`
- `Metric Snapshot`
- `Lifecycle Event`
- `AI Agent Adapter`
- `AI Analysis Session`

## Architectural Direction

The project should follow a clean architecture or equivalent layered architecture where:

- business rules remain independent from delivery mechanisms
- CLI, API, and interface layers act as adapters
- project-specific runtime integrations are accessed through `Project Adapter` contracts
- AI providers are accessed through adapters instead of core-domain coupling
- infrastructure concerns remain outside core domain logic
- persistence and external integrations can evolve without rewriting the domain model

## Physical Boundary Direction

The project structure should preserve clear physical separation between:

- the backend core and its internal layers
- external operational surfaces such as CLI and API
- interface clients that consume the API

The `interface/` folder should act as a physical boundary for user-facing clients such as:

- `web`
- `mobile`
- `desktop`

These interface clients should consume the API rather than bypassing the backend architecture.

## Persistence Direction

`SQLite` is the initial persistence candidate because it supports a lightweight local-first workflow while still allowing robust enough storage for users, projects, permissions, lifecycle metadata, and audit events.

For `v0.2.0`, the selected backend persistence stack is `SQLite` with `SQLAlchemy` and `Alembic`.

## Selected Technology Direction

The project currently adopts the following implementation direction:

- backend language: `Python`
- package and environment management: `uv`
- CLI adapter: `Typer`
- API adapter: `FastAPI`
- persistence: `SQLite`
- ORM and migrations: `SQLAlchemy` and `Alembic`
- authentication: JWT plus password hashing with `bcrypt`
- backend quality tooling: `pytest`, `ruff`, and `mypy`
- frontend package manager: `pnpm`
- web interface layer: `React`, `TypeScript`, and `Vite`

## Delivery Expectation

The project should evolve in this order:

1. documentation foundation
2. core source architecture
3. external adapters for CLI and API
4. interface layer

## Quality Expectations

- explicit operational contracts
- low ambiguity
- traceable lifecycle actions
- maintainable architecture
- minimal duplication of business rules
- documentation-code alignment
