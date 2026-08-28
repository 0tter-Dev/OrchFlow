# Documentation Index

## Purpose

This index explains how the documentation is organized and how the major product capabilities connect to one another.

## Reading Order

1. [Project Architecture](./PROJECT-ARCHITECTURE.md)
2. [Development Guide](./DEVELOPMENT-GUIDE.md)
3. [Feature Status](./STATUS.md)
4. Context documents in `docs/context/`
5. [User Guide](./USER-GUIDE.md)

## Documentation Map

- [Project Architecture](./PROJECT-ARCHITECTURE.md)
Defines product purpose, rules, scope, boundaries, and core architectural direction.

- [Development Guide](./DEVELOPMENT-GUIDE.md)
Defines engineering rules, design expectations, change boundaries, and future implementation discipline.

- [Feature Status](./STATUS.md)
Tracks feature implementation state at a high level.

- [User Guide](./USER-GUIDE.md)
Shows how a user is expected to interact with OrchFlow through a realistic end-to-end workflow.

- [Git And GitHub Flow](./GIT-GITHUB-FLOW.md)
Defines the repository workflow, pull request discipline, versioning model, CI direction, and GitHub configuration standard.

- `docs/context/`
Contains feature-oriented context documents that describe purpose, scope, planned behavior, interactions, and implementation status.

## Context Connections

- [Access Control](./context/access-control.md)
Defines users, roles, activation, permissions, and how access decisions affect project visibility and actions.

- [Project Registry](./context/project-registry.md)
Defines how projects are registered, identified, owned, assigned, and persisted.

- [Project Adapter](./context/project-adapter.md)
Defines the generic adapter layer used to connect OrchFlow to different managed projects.

- [Lifecycle Orchestration](./context/lifecycle-orchestration.md)
Defines lifecycle actions, state transitions, and operational control behavior.

- [Lifecycle Script Template](./context/lifecycle-script-template.md)
Defines the standard `.bat` contract shape and ideal lifecycle function model used by managed projects.

- [Runtime Inspection](./context/runtime-inspection.md)
Defines how OrchFlow inspects ports, processes, uptime, resource usage, status explanations, and URL reachability.

- [AI Assistance Adapter](./context/ai-agent-adapter.md)
Defines the optional AI assistance adapter layer, including the planned LiteLLM gateway integration, for analyzing a folder and helping produce a reviewable lifecycle `.bat` script.

- [Configuration And Environment](./context/configuration-and-environment.md)
Defines the environment-based configuration contract and `.env` direction.

- [External Surfaces](./context/external-surfaces.md)
Defines how CLI and API mirror the same application capabilities.

- [Interface Layer](./context/interface-layer.md)
Defines the API-consuming interface boundary for web, mobile, and desktop clients.

- [Persistence And Audit](./context/persistence-and-audit.md)
Defines local storage direction, lifecycle event history, and admin audit visibility.

- [DevOps And Delivery](./context/devops-and-delivery.md)
Defines source-control, validation, and CI/CD expectations.

## Relationship Overview

`Access Control` governs who can see and control a `Project`, including admin user-management rules.

`Project Registry` stores and normalizes the metadata needed for a project to exist inside OrchFlow, including project ownership assignments, lifecycle action mappings, and lifecycle function configuration state.

`Project Adapter` gives `Lifecycle Orchestration` a generic boundary for project-specific execution behavior.

`Lifecycle Orchestration` depends on `Project Registry` to retrieve the lifecycle script definition and project metadata.

`Lifecycle Script Template` defines the standardized `.bat` shape and ideal lifecycle function model expected by `Project Registry`, `Project Adapter`, and `AI Assistance Adapter`.

`Runtime Inspection` supports `Lifecycle Orchestration` by validating whether actions succeeded and by producing runtime facts and diagnostic explanations for operators.

`AI Assistance Adapter` supports `Project Registry` by helping a user transform a project folder into a reviewable `.bat` lifecycle script and, when needed, suggest action mappings. LiteLLM is planned as the provider/model gateway inside that adapter, while OrchFlow remains responsible for authorization, allowed context, validation, and final approval.

Project reload workflows should let users explicitly reread one or more lifecycle scripts, refresh automatic function detection, compare the project against the ideal lifecycle model, and decide whether to update mappings manually or ask AI assistance for improvements.

`Configuration And Environment` provides validated runtime settings to infrastructure services and external adapters without leaking config rules into the domain.

`External Surfaces` expose use cases from the core application without redefining business logic.

`Interface Layer` depends on the API-facing surface for data presentation and control actions across different client implementations.

`Persistence And Audit` supports all core modules by storing users, permissions, projects, lifecycle events, and recent audit history for admin review.

`DevOps And Delivery` governs how the project itself is built, reviewed, tested, and released.
