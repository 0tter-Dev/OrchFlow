---
id: web-006
status: completed
type: docs
requires_pull_request: true
expected_version_impact: none
authorized_capabilities:
  - capabilities/web-operator-workspace/README.md
  - capabilities/project-registry/README.md
decision_records:
  - decisions/ADR-0001-local-first-bat-lifecycle-contract.md
validation:
  - documentation-structure-test
  - markdown-link-check
documentation_updates:
  - docs/PROJECT-ARCHITECTURE.md
  - docs/reference/external-surfaces.md
---

# Local Path-Selection Contract

## Objective

Define the reviewed local-backend contract required for choosing a project folder or lifecycle script from the web onboarding flow.

## Context

A browser file picker cannot reliably provide an absolute path usable by the local backend. A native Windows dialog would introduce an authenticated public API and audit/security responsibilities. The requesting user explicitly approved activation and implementation on 2026-09-12.

## Decisions

Document a local-only, authenticated backend contract that invokes a native folder or script dialog and returns only the user-selected path. Browser-only picker APIs, Electron, Tauri, and generic picker dependencies are not substitutes.

## Scope

Produce the architecture, API, authorization, audit, error, cancellation, and path-disclosure decision needed before implementation.

## Out Of Scope

Implementing an endpoint, dialog, or web control.

## Acceptance Criteria

The approved contract states its local-only boundary, authenticated caller, returned data, audit behavior, and failure cases.

## Validation

Review links, documentation structure, and the proposed public-contract decision.

## Documentation Updates

Update architecture, external-surface reference, relevant capability documents, and ADRs if the decision is durable.

## Outcome

Completed contract definition; implementation remains deferred to `web-007`.
