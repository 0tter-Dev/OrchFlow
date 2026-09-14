---
id: web-012
status: completed
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

Implemented in commit `4f0cedb` and merged through [PR #69](https://github.com/0tter-Dev/OrchFlow/pull/69) on `2026-09-13`. The user approved `@playwright/test` and its Chromium installation. The merged browser suite established deterministic account creation and authenticated project registration with path selection; a post-merge workflow timeout in the lifecycle-confirmation browser assertion was remediated by retaining those stable browser journeys and verifying the mutable-action confirmation deterministically at component level. Validation includes frontend lint, frontend tests, frontend build, the two Playwright browser workflows, and 5 documentation-structure tests. No release version change is required.
