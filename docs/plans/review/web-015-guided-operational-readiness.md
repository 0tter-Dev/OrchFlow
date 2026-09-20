---
id: web-015
status: review
type: feat
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: patch
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

## Approval

The requesting user explicitly approved activation and implementation on 2026-09-19.

## Acceptance Criteria

- the workspace distinguishes complete, partial, blocked, and unavailable states with explanations;
- each state points to a permitted, contextual next action;
- configuration diagnostics use the redacted cfg-002 contract;
- partial projects remain usable for configured actions;
- browser tests cover a recovery journey from a blocked/partial state.

## Outcome

Implemented on the delivery branch and awaiting review in
[PR #80](https://github.com/0tter-Dev/OrchFlow/pull/80).

- Delivery commits: `f77b3a5`, `99e2850`, `f9f4949`, `4e142a8`, and `9c0cdeb`.
- Expected and actual version impact: `patch`, advancing `0.3.42` to `0.3.43`.
- Validation passed: frontend lint, 52 frontend unit tests, production build, and
  three deterministic Playwright workflows (account creation, project registration
  with local path selection, and blocked-project mapping recovery); backend Ruff
  and mypy; and eight documentation/version contract tests.
- The selected-project checklist composes existing lifecycle and runtime signals
  with only the redacted remediation supplied by configuration health. It retains
  direct reload, mapping, and runtime-refresh actions without treating browser
  state as authoritative or exposing local values and secrets.
