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
- project update, project reload, and lifecycle function mapping flows should be mirrored in CLI and API when implemented
- audit history visibility should be introduced in both surfaces together so operational review remains consistent
- AI assistance workflows should be introduced in CLI and API together when intentionally exposed, with the API remaining the boundary consumed by web
- business logic must stay in the core application, not in the delivery layer
- authorization rules must be enforced consistently
- the API should be the primary backend entry point for interface clients
- CLI and API must not call LiteLLM directly; they should call OrchFlow application services that enforce context scope, authorization, validation, and review

## Implemented Baseline

- CLI and API both expose authentication, project registry, non-AI project updates, configured-action lifecycle execution, runtime inspection, filtered admin audit history visibility, admin user updates, project owner management, manual lifecycle configuration, project reload, and AI assistance workflows. The web interface consumes existing contracts for project editing, project configuration health, action gating, reload, mapping updates, AI proposal review/application, and audit troubleshooting.
- lifecycle responses now include a summarized runtime status when inspection is available
- direct runtime inspection is available through `GET /projects/{project_id}/runtime` and the mirrored CLI command `runtime inspect`, including status explanation, inspection timestamp, `APP_URL` reachability when available, `APP_URL`-only running detection, and clearer timeout or unsupported diagnostics
- the first `interface/web` operator flow now consumes these same contracts for sign-in, project visibility, runtime inspection, lifecycle controls, project registration, AI proposal review/application, filtered admin audit history, and richer API or validation error notices

External surfaces now include API and CLI workflows for updating project metadata and lifecycle script paths, manual mapping updates, explicit unconfigured-function decisions, explicit reload for one or more projects, AI-assisted improvement proposal workflows, and clear lifecycle execution rejection when an action is undefined, explicitly unconfigured, or part of a blocked project. The web operator surface now combines those contracts into a guided operational readiness panel for selected projects and preserves backend failure details in contextual error notices. Planned refinements include broader web operator experience polish.

## Current API Inventory

The current implemented API surface includes:

- system: `GET /`, `GET /health`, `GET /system/config`, `GET /system/database`
- authentication: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`, `GET /auth/users`, `PATCH /auth/users/{user_id}`
- audit: `GET /audit/events`
- AI assistance: `GET /ai/status`, `GET /ai/gateway/health`, `GET /ai/models`, `POST /ai/context-manifests`, `GET /ai/context-manifests/{manifest_id}`, `POST /ai/analysis-proposals`, `GET /ai/analysis-proposals/{proposal_id}`, `POST /ai/analysis-proposals/{proposal_id}/review`, `POST /ai/analysis-proposals/{proposal_id}/apply`
- projects: `POST /projects`, `GET /projects`, `GET /projects/{project_id}`, `PATCH /projects/{project_id}`, `PATCH /projects/{project_id}/lifecycle-configuration`, `POST /projects/{project_id}/reload`, `POST /projects/reload`, `POST /projects/{project_id}/owners/{user_id}`, `DELETE /projects/{project_id}/owners/{user_id}`
- lifecycle and runtime: `POST /projects/{project_id}/lifecycle/{action}`, `GET /projects/{project_id}/runtime`

## Current CLI Inventory

The current implemented CLI surface includes:

- system commands: `orchflow info`, `orchflow health`, `orchflow config`, `orchflow database`
- authentication commands: `orchflow auth register`, `orchflow auth login`, `orchflow auth me`, `orchflow auth users`, `orchflow auth update-user`
- project commands: `orchflow project register`, `orchflow project list`, `orchflow project show`, `orchflow project update`, `orchflow project configure-lifecycle`, `orchflow project reload`, `orchflow project reload-many`, `orchflow project add-owner`, `orchflow project remove-owner`
- lifecycle commands: `orchflow lifecycle status`, `orchflow lifecycle start`, `orchflow lifecycle stop`, `orchflow lifecycle restart`
- runtime command: `orchflow runtime inspect`
- audit command: `orchflow audit events`
- AI assistance commands: `orchflow ai status`, `orchflow ai health`, `orchflow ai models`, `orchflow ai manifest-create`, `orchflow ai manifest-show`, `orchflow ai proposal-create`, `orchflow ai proposal-show`, `orchflow ai proposal-review`, `orchflow ai proposal-apply`

## Main Relationships

- depends on `Access Control`
- depends on `Project Registry`
- depends on `Lifecycle Orchestration`
- depends on `Runtime Inspection`
- may expose `AI Assistance Adapter` workflows
- may expose LiteLLM-backed AI assistance workflows only through the OrchFlow adapter boundary
