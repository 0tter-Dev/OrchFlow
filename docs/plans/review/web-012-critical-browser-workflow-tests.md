---
id: web-012
status: review
type: test
requires_pull_request: true
expected_version_impact: none
actual_version_impact: none
priority: medium
sequence: 6
depends_on:
  - web-007
  - web-008
  - web-009
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

Implemented in commit `4f0cedb` and delivered through [PR #69](https://github.com/0tter-Dev/OrchFlow/pull/69). The user approved `@playwright/test` and its Chromium installation; the browser suite covers deterministic account creation, authenticated project registration with path selection, and confirmation before mutable lifecycle actions. Validation passed: frontend lint, 50 frontend tests, frontend build, 3 Playwright browser workflows, and 5 documentation-structure tests. No release version change is required. Awaiting review and merge.
