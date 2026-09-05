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
- user roles and project ownership
- operational history
- external access through CLI, API, and interface layers

## Core Principle

In `v0.3.22`, every managed project must have a concrete lifecycle control definition based on a Windows `.bat` script. This script is the authoritative operational contract used by OrchFlow to control the project lifecycle.

The AI assistance layer is optional and assistive. Its integration model uses `LiteLLM` as the central gateway for connecting to local or configured AI models and agents, while OrchFlow keeps a dedicated adapter boundary responsible for context selection, file access control, authorization, validation, review workflow, and final user approval. The implemented boundary reports authenticated, audited LiteLLM configuration status, gateway health, model discovery, authorized context manifests, reviewable analysis proposals, proposal review decisions, explicit application of approved proposals, and web review/application controls. Proposal creation may send only manifest-approved context to LiteLLM and persists structured proposal data without writing `.bat` files. Proposal approval validates the candidate `.bat` script against first-argument dispatch, required canonical actions, and proposed mapping consistency. Proposal application is a separate confirmed step that writes or overwrites the lifecycle `.bat`, persists effective mappings as `ai_approved`, records a dedicated application record, and reuses Project Registry validation before the project becomes operational. LiteLLM may connect to providers such as local `Ollama` or other explicitly configured model backends, but it must not replace the explicit `.bat` script contract or OrchFlow's business rules.

## Goals

- Provide a standardized local orchestration workflow for multiple projects
- Support registration of user-owned projects with explicit lifecycle control definitions
- Offer lifecycle operations such as status, start, stop, and restart
- Expose runtime data such as ports, process identifiers, uptime, CPU, and memory
- Support both command-line and programmatic access through mirrored external interfaces
- Provide a compact visual operator workspace for fast inspection and lifecycle control
- Enforce authentication and authorization through application users, roles, and project ownership
- Establish a disciplined engineering foundation for Git, GitHub, testing, and CI

## Non-Goals For v0.3.22

- Container orchestration
- Multi-host orchestration
- Automatic download or installation of AI models
- Direct autonomous AI control over project lifecycle actions
- Replacing explicit lifecycle scripts with AI-managed automation
- Full observability platform capabilities
- Distributed agents acting without user supervision

These non-goals should not be treated as a reason to hard-couple the codebase against future evolution, but OrchFlow should not introduce container-oriented behavior or architecture detail unless a later product decision explicitly requires it.

## Primary Actors

- `member`: a regular user who can manage projects they own
- `admin`: a privileged user with full platform access, including user visibility, role management, and project ownership management

## Business Rules

### Project Ownership

- Each project must have a user-facing reference name
- Each project must be associated with one or more authorized users
- In the current implementation, project-level authorization is represented through ownership assignments plus the `admin` role, not through a separate generic permission table
- Ownership and role-based access rules must be enforced consistently across CLI, API, and interface channels

### Lifecycle Control

- OrchFlow must support at least `status`, `start`, `stop`, and `restart`
- OrchFlow must define an ideal lifecycle function model that describes the expected project capabilities and their purpose
- Lifecycle actions must be routed through a normalized project definition
- lifecycle execution must pass through a generic `Project Adapter` boundary
- OrchFlow should use canonical lifecycle actions internally even when projects expose different script labels
- project-specific metadata, script paths, action mappings, and lifecycle function configuration states must be editable, persistable, reviewable, and auditable
- lifecycle functions should be classified as `configured`, `unconfigured`, or `undefined` from the operator's perspective
- `configured` means OrchFlow has an automatic or manual mapping from an ideal lifecycle function to a concrete script command
- `undefined` means OrchFlow has not detected a mapping and the user has not made an explicit decision
- `unconfigured` means the user explicitly chose not to configure that ideal lifecycle function for the project
- projects with at least one configured lifecycle function may remain usable for their configured actions, even when they do not fully match the ideal model
- projects where every lifecycle function is either undefined or unconfigured must be treated as not operationally controllable and should be blocked until at least one function is configured
- lifecycle execution must reject undefined or explicitly unconfigured actions instead of assuming default script identifiers
- projects with partial lifecycle configuration should present an operator-facing warning and improvement path rather than being blocked
- projects with every ideal lifecycle function configured should be identified as having complete lifecycle configuration
- Lifecycle operations must be auditable
- Runtime inspection must not be implemented as a UI-only concern
- users should be able to explicitly reload one or more registered projects so OrchFlow can reread lifecycle scripts, refresh detected functions, preserve valid user decisions, surface changed mappings, and audit configuration-health changes without relying on automatic filesystem watching

### User Preferences

- authenticated users should be able to persist lightweight interface preferences such as locale, project display mode, and status refresh interval
- user preferences are scoped to the authenticated user and should be exposed through backend contracts consumed by interface clients
- preference persistence must remain optional to operational control and must not affect project authorization or lifecycle execution rules

### AI Agent Assistance

- AI analysis is optional
- OrchFlow must mediate all AI interactions through an AI assistance adapter owned by the application layer
- `LiteLLM` is the central LLM gateway for provider and model connectivity
- OrchFlow must not call `LiteLLM` directly from delivery adapters or domain rules
- API and CLI may expose only OrchFlow application-service AI workflows; implemented status, gateway health, and model discovery checks must not send project context or execute prompts
- local `Ollama` should be supported through the LiteLLM integration path when enabled, but the architecture must remain provider-agnostic
- AI assistance must operate only against resources already available and authorized on the machine
- OrchFlow may start or verify a local provider process only through explicit configuration and user-authorized workflows
- OrchFlow must not download new models automatically
- the user must explicitly authorize project inspection before AI analysis starts
- the user must explicitly authorize creation or overwrite of a lifecycle `.bat` file
- the user must explicitly authorize persistence of AI-suggested action mappings
- AI suggestions and generated files must be reviewable by the user before becoming part of a project definition
- LiteLLM output must be treated as a proposal, not verified runtime truth

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
- persist authenticated user preferences used by interface clients
- authenticate users
- authorize access to projects and actions
- mediate optional AI-assisted project analysis and script generation
- expose consistent operational capabilities through CLI, API, and interface adapters

OrchFlow should not, in `v0.3.22`:

- behave as a container orchestrator
- assume remote infrastructure control
- infer production-grade deployment logic from local project folders
- treat AI inference as authoritative runtime control

The implementation should avoid speculative abstractions for possible future container support. If that support is ever considered later, it should be introduced through an explicit product decision rather than preemptive design.

## Initial Domain Concepts

- `User`
- `Project Ownership`
- `Project`
- `Project Adapter`
- `Project Lifecycle Script`
- `Lifecycle Action Mapping`
- `Ideal Lifecycle Function Model`
- `Lifecycle Function Configuration State`
- `Lifecycle Script Template`
- `Project Definition`
- `Project Reload`
- `Runtime Snapshot`
- `Metric Snapshot`
- `Lifecycle Event`
- `User Preferences`
- `AI Assistance Adapter`
- `LiteLLM Gateway`
- `AI Analysis Session`

## Architectural Direction

The project should follow a clean architecture or equivalent layered architecture where:

- business rules remain independent from delivery mechanisms
- CLI, API, and interface layers act as adapters
- project-specific runtime integrations are accessed through `Project Adapter` contracts
- AI providers are accessed through the OrchFlow AI assistance adapter, with LiteLLM isolated as an infrastructure gateway rather than coupled to core-domain rules
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

`SQLite` is the initial persistence candidate because it supports a lightweight local-first workflow while still allowing robust enough storage for users, user preferences, projects, ownership metadata, lifecycle metadata, and audit events.

For `v0.3.22`, the selected backend persistence stack is `SQLite` with `SQLAlchemy` and `Alembic`.

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
- AI/model gateway: `LiteLLM`, isolated behind the OrchFlow AI assistance adapter

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
