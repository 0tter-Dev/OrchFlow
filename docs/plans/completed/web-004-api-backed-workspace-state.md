---
id: web-004
status: completed
type: refactor
requires_pull_request: true
expected_version_impact: none
authorized_capabilities:
  - capabilities/web-operator-workspace/README.md
decision_records: []
validation:
  - frontend-lint
  - frontend-test
  - frontend-build
documentation_updates:
  - docs/STATUS.md
---

# API-Backed Workspace State

## Objective

Adopt `@tanstack/react-query` for server state while preserving current operational behavior.

## Context

Health, project lists, refreshes, and mutations currently need consistent caching, invalidation, retry, and latest-known-good behavior. The requesting user explicitly approved activation and implementation on 2026-09-12. This plan authorizes only `capabilities/web-operator-workspace/README.md` as feature context.

## Decisions

Start with health and project-list state; define stable query keys and invalidate affected views after lifecycle actions. Do not add Redux, Zustand, or another global state library without a separate proven need.

## Scope

Add the query client and progressively migrate selected API-backed state.

## Out Of Scope

New backend endpoints, authorization changes, or broad UI redesign.

## Acceptance Criteria

Refresh failures preserve the latest valid health snapshot and successful mutations refresh affected data predictably.

## Validation

Run frontend validation and targeted tests for loading, error, and post-mutation states.

## Documentation Updates

Update the web capability and status only if observable refresh behavior changes.

## Outcome

Implemented and delivered through [PR #59](https://github.com/0tter-Dev/OrchFlow/pull/59).

- Added a shared `@tanstack/react-query` client for web server state.
- Migrated health state to a stable query key that preserves the latest successful snapshot through refetch failure.
- Routed project-list retrieval through the shared cache and invalidate it after project and lifecycle mutations.
- Added a focused health-state retention test.
- Version impact: none; this refactor preserves public contracts and workflows.
- Commit: `d1793d4` (`refactor(web): add API-backed workspace state`).
