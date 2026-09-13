---
id: web-007
status: active
type: feat
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: pending
priority: high
sequence: 1
depends_on: []
authorized_capabilities:
  - capabilities/web-operator-workspace/README.md
  - capabilities/project-registry/README.md
decision_records: []
validation:
  - backend-test
  - api-contract-test
  - frontend-test
  - frontend-build
documentation_updates:
  - docs/STATUS.md
  - docs/guides/user-guide.md
  - docs/reference/external-surfaces.md
---

# Local Path-Selection Workflow

## Objective

Implement approved local folder and lifecycle-script selection in project onboarding.

## Context

This plan depends on the completed and explicitly approved `web-006` contract.

## Decisions

Use only the approved authenticated local-backend contract; keep manual path entry available and preserve backend validation as authoritative.

## Scope

Add the approved backend route, authorization and audit behavior, Windows dialog integration, web controls, and tests.

## Out Of Scope

Remote path browsing, filesystem crawling, desktop-shell migration, and changes to lifecycle execution semantics.

## Acceptance Criteria

An authorized operator can select a local path, cancel safely, understand errors, and complete existing validation without exposing unselected paths.

## Validation

Run relevant backend/API/frontend suites and manually test successful, cancelled, and unauthorized cases.

## Documentation Updates

Update owning capabilities, external-surface reference, user guide, status, and version references.

## Outcome

Approved by the user in this thread to begin implementation and deliver one pull request. Delivery is in progress.
