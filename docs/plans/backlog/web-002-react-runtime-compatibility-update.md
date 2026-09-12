---
id: web-002
status: backlog
type: chore
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

# React Runtime Compatibility Update

## Objective

Update `react` and `react-dom` as one tested compatibility unit.

## Context

The runtime must remain compatible with the current React type packages, Radix primitives, and test environment.

## Decisions

Select a compatible React 19 maintenance release only after reviewing peer dependencies and release notes. React type packages were updated in `web-001` and must be validated rather than unnecessarily changed again.

## Scope

Update the runtime dependency group and resolve compatibility findings in current web flows.

## Out Of Scope

Navigation redesign, new state management, and Vite or TypeScript major upgrades.

## Acceptance Criteria

Authenticated and unauthenticated flows, current primitives, lint, tests, and production build remain functional.

## Validation

Run the complete frontend validation suite and manually exercise login and workspace startup.

## Documentation Updates

Update status and version references only when justified by the delivered behavior.

## Outcome

Backlog candidate; not started.
