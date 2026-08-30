# External Surfaces

## Purpose

This module defines the non-visual delivery channels that expose OrchFlow capabilities.

## Objective

Expose the same core application behavior through both CLI and API without duplicating business rules.

## Current Status

`in_progress`

## Channels

- `CLI`
- `API`

## Key Rules

- CLI and API should mirror the same core use cases as closely as practical
- CLI and API bootstrap work should evolve together whenever a capability is intentionally exposed by one of them
- authentication and authorization flows should be introduced in both surfaces together so access-control behavior remains consistent
- lifecycle control actions should be introduced in both surfaces together so project operations remain consistent
- runtime inspection flows should be introduced in both surfaces together so operational visibility remains consistent
- project reload and lifecycle function mapping flows should be mirrored in CLI and API when implemented
- audit history visibility should be introduced in both surfaces together so operational review remains consistent
- AI assistance workflows should be introduced in CLI and API together when intentionally exposed, with the API remaining the boundary consumed by web
- business logic must stay in the core application, not in the delivery layer
- authorization rules must be enforced consistently
- the API should be the primary backend entry point for interface clients
- CLI and API must not call LiteLLM directly; they should call OrchFlow application services that enforce context scope, authorization, validation, and review

## Implemented Baseline

- CLI and API both expose authentication, project registry, configured-action lifecycle execution, runtime inspection, admin audit history visibility, admin user updates, project owner management, manual lifecycle configuration, and project reload. The web interface consumes those contracts for project configuration health, action gating, reload, and mapping updates.
- lifecycle responses now include a summarized runtime status when inspection is available
- direct runtime inspection is available through `GET /projects/{project_id}/runtime` and the mirrored CLI command `runtime inspect`, including status explanation, inspection timestamp, and `APP_URL` reachability when available
- the first `interface/web` operator flow now consumes these same contracts for sign-in, project visibility, runtime inspection, lifecycle controls, project registration, and admin audit history

External surfaces now include API and CLI workflows for manual mapping updates, explicit unconfigured-function decisions, explicit reload for one or more projects, and clear lifecycle execution rejection when an action is undefined, explicitly unconfigured, or part of a blocked project. Planned refinements include richer lifecycle function configuration indicators and AI-assisted improvement proposal workflows.

## Main Relationships

- depends on `Access Control`
- depends on `Project Registry`
- depends on `Lifecycle Orchestration`
- depends on `Runtime Inspection`
- may expose `AI Assistance Adapter` workflows
- may expose LiteLLM-backed AI assistance workflows only through the OrchFlow adapter boundary
