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

- `docs/context/`
Contains feature-oriented context documents that describe purpose, scope, planned behavior, interactions, and implementation status.

## Context Connections

- [Access Control](./context/access-control.md)
Defines users, roles, permissions, and how access decisions affect project visibility and actions.

- [Project Registry](./context/project-registry.md)
Defines how projects are registered, identified, owned, and persisted.

- [Lifecycle Orchestration](./context/lifecycle-orchestration.md)
Defines lifecycle actions, state transitions, and operational control behavior.

- [Runtime Inspection](./context/runtime-inspection.md)
Defines how OrchFlow inspects ports, processes, uptime, and resource usage.

- [AI Agent Adapter](./context/ai-agent-adapter.md)
Defines the optional AI adapter layer for analyzing a folder and helping produce a lifecycle `.bat` script.

- [External Surfaces](./context/external-surfaces.md)
Defines how CLI and API mirror the same application capabilities.

- [Interface Layer](./context/interface-layer.md)
Defines the simple visual interface and how it depends on platform services.

- [Persistence And Audit](./context/persistence-and-audit.md)
Defines local storage direction and lifecycle event history.

- [DevOps And Delivery](./context/devops-and-delivery.md)
Defines source-control, validation, and CI/CD expectations.

## Relationship Overview

`Access Control` governs who can see and control a `Project`.

`Project Registry` stores and normalizes the metadata needed for a project to exist inside OrchFlow.

`Lifecycle Orchestration` depends on `Project Registry` to retrieve the lifecycle script definition and project metadata.

`Runtime Inspection` supports `Lifecycle Orchestration` by validating whether actions succeeded and by producing runtime facts for operators.

`AI Agent Adapter` supports `Project Registry` by helping a user transform a project folder into a reviewable `.bat` lifecycle script.

`External Surfaces` expose use cases from the core application without redefining business logic.

`Interface Layer` depends on the API-facing surface for data presentation and control actions.

`Persistence And Audit` supports all core modules by storing users, permissions, projects, and lifecycle events.

`DevOps And Delivery` governs how the project itself is built, reviewed, tested, and released.
