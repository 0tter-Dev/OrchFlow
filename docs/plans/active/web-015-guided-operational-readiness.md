---
id: web-015
status: backlog
type: feat
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: pending
priority: high
sequence: 14
depends_on:
  - cfg-002
authorized_capabilities:
  - capabilities/web-operator-workspace/README.md
  - capabilities/configuration/README.md
decision_records: []
validation:
  - frontend-lint
  - frontend-test
  - frontend-build
  - critical-browser-workflow-test
documentation_updates:
  - docs/capabilities/web-operator-workspace/README.md
  - docs/guides/user-guide.md
---

# Guided Project Operational Readiness

## Objective

Turn the existing project readiness signals into a focused, ordered recovery path inside the authenticated web workspace.

## Scope

Compose already-authoritative backend data for project registration, lifecycle script validity, lifecycle mappings, safe configuration health, and runtime inspection into one project-level readiness sequence. Present the appropriate next action — reload, configure mappings, correct local configuration, refresh runtime, or run a configured action — without inferring lifecycle behavior.

## Out Of Scope

Browser editing of secrets, UI-only readiness decisions, automatic project control, remote orchestration, or replacing the `.bat` lifecycle contract.

## Acceptance Criteria

- the workspace distinguishes complete, partial, blocked, and unavailable states with explanations;
- each state points to a permitted, contextual next action;
- configuration diagnostics use the redacted cfg-002 contract;
- partial projects remain usable for configured actions;
- browser tests cover a recovery journey from a blocked/partial state.

## Outcome

Backlog candidate; not started.
