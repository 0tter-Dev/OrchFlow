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
- audit history visibility should be introduced in both surfaces together so operational review remains consistent
- business logic must stay in the core application, not in the delivery layer
- authorization rules must be enforced consistently
- the API should be the primary backend entry point for interface clients

## Implemented Baseline

- CLI and API both expose authentication, project registry, lifecycle execution, runtime inspection, and admin audit history visibility
- lifecycle responses now include a summarized runtime status when inspection is available
- direct runtime inspection is available through `GET /projects/{project_id}/runtime` and the mirrored CLI command `runtime inspect`
- the first `interface/web` operator flow now consumes these same contracts for sign-in, project visibility, runtime inspection, lifecycle controls, project registration, and admin audit history

## Main Relationships

- depends on `Access Control`
- depends on `Project Registry`
- depends on `Lifecycle Orchestration`
- depends on `Runtime Inspection`
- may expose `AI Agent Adapter` workflows
