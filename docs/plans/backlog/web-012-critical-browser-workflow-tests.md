---
id: web-012
status: backlog
type: test
requires_pull_request: true
expected_version_impact: none
authorized_capabilities:
  - capabilities/web-operator-workspace/README.md
decision_records: []
validation:
  - frontend-lint
  - frontend-test
  - browser-workflow-test
documentation_updates:
  - docs/STATUS.md
---

# Critical Browser Workflow Tests

## Objective

Evaluate Playwright and add end-to-end coverage for stabilized critical web workflows.

## Context

Component and contract tests cannot fully validate authenticated navigation, onboarding, confirmation, and browser integration together.

## Decisions

Introduce Playwright only after navigation and project onboarding flows stabilize; keep it separate from the feature PRs it verifies.

## Scope

Cover login/account creation, project registration, lifecycle-action confirmation, and path selection when that approved workflow exists.

## Out Of Scope

Broad visual-regression infrastructure or testing unimplemented future flows.

## Acceptance Criteria

Critical user journeys run deterministically in CI or documented local validation without leaking local credentials or paths.

## Validation

Run the selected browser suite with existing frontend validation.

## Documentation Updates

Update testing guidance and status when browser coverage is adopted.

## Outcome

Backlog candidate; depends on stabilized workflows.
