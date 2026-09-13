---
id: web-010
status: completed
type: feat
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: patch
priority: medium
sequence: 4
depends_on: []
authorized_capabilities:
  - capabilities/web-operator-workspace/README.md
  - capabilities/persistence-and-audit/README.md
decision_records: []
validation:
  - frontend-lint
  - frontend-test
  - frontend-build
documentation_updates:
  - docs/STATUS.md
  - docs/guides/user-guide.md
---

# Advanced Operational Tables

## Objective

Evaluate and, only when justified, add `@tanstack/react-table` for complex project or audit views.

## Context

Simple filters and sorting should be delivered first. A table library is useful only when composable columns, pagination, visibility, or richer filtering become a demonstrated need.

## Decisions

Keep authorization and canonical filtering in the API; use the library only for client presentation behavior.

## Scope

Assess concrete list complexity and implement a focused table only if it has clear operator value.

## Out Of Scope

Replacing backend filtering/authorization or adding tables solely for visual convention.

## Acceptance Criteria

The selected view has a demonstrated need and offers accessible, understandable sorting/filtering without hiding operational state.

## Validation

Run frontend validation and tests for the selected table behavior.

## Documentation Updates

Update user guidance, capability status, and version references if implemented.

## Outcome

Implemented through [PR #67](https://github.com/0tter-Dev/OrchFlow/pull/67), merged on 2026-09-13. The implementation added the accessible operational project table using the legacy-compatible TanStack Table API, with sorting and filtering retained as client presentation behavior. Version `0.3.34` advanced to `0.3.35`; the merge commit is `f487f3fb54565ab37fb3a3e5d921628551e29f68`. Validation completed with frontend lint, 49 frontend tests, and frontend build.
