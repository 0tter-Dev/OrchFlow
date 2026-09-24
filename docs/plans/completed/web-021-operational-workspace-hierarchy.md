---
id: web-021
status: completed
type: feat
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: pending
priority: medium
sequence: 20
depends_on:
  - web-020
authorized_capabilities:
  - capabilities/web-operator-workspace/README.md
  - capabilities/project-registry/README.md
  - capabilities/runtime-inspection/README.md
  - capabilities/persistence-and-audit/README.md
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

# Operational Workspace Hierarchy

## Objective

Refine Projects into a direct desktop operator flow where the selected project, its state, available actions, and next recovery step are evident without scanning a dense page.

## Approval

The requesting user explicitly approved activation and implementation on 2026-09-23.

## Scope

- establish the repeatable hierarchy of project selection, concise operational summary, lifecycle actions, runtime evidence, configuration, and contextual history;
- improve list and table presentation so filtering, sorting, selection, and state indicators remain useful without duplicating detail;
- use focused dialogs only for short confirmations or contained details, leaving multi-field registration and long-lived configuration in a workspace surface;
- normalize empty, loading, partial-readiness, unsupported-runtime, and error states into concise guidance with a clear next action;
- preserve project authorization, lifecycle controls, audit authority, and the completed registration-reliability behavior.

## Out Of Scope

Changing authorization, a general dashboard-builder, mobile-first redesign, or replacing canonical project detail with unstructured modal screens.

## Acceptance Criteria

- an operator can identify the selected project's state and next useful action from primary content;
- list/table and detail have distinct, non-redundant responsibilities;
- dialogs are keyboard-accessible, reversible where appropriate, and do not hide essential controls;
- representative empty, error, and ready states pass browser and accessibility-oriented tests.

## Outcome

Delivered in PR #88, merged into synchronized `main` on 2026-09-23. The selected-project workspace now leads with runtime evidence and a contextual next action; frontend and browser validation passed.
