---
id: web-008
status: backlog
type: feat
requires_pull_request: true
expected_version_impact: patch
authorized_capabilities:
  - capabilities/web-operator-workspace/README.md
  - capabilities/project-registry/README.md
decision_records: []
validation:
  - frontend-lint
  - frontend-test
  - frontend-build
documentation_updates:
  - docs/STATUS.md
  - docs/guides/user-guide.md
---

# Guided Project Forms

## Objective

Add structured project registration and editing forms with `react-hook-form` and `zod`.

## Context

The project workflow needs field-level feedback, typed form state, draft preservation, and clearer progression without duplicating backend business validation.

## Decisions

Adopt `react-hook-form` and `zod`; add only needed Radix primitives for dialog, alert dialog, dropdown menu, and select. Decide on a toast primitive only after evaluating the existing notification pattern.

## Scope

Create guided form flows, client-side validation, drafts, and accessible dialogs around existing registration and edit contracts.

## Out Of Scope

Changing server validation, lifecycle rules, or adding a generic UI framework.

## Acceptance Criteria

Operators receive actionable field feedback, retain entered values across recoverable errors, and can complete current project workflows accessibly.

## Validation

Run frontend validation and form tests for valid, invalid, cancelled, and server-rejected submissions.

## Documentation Updates

Update owning capabilities, user guide, status, and version references as required.

## Outcome

Backlog candidate; not started.
