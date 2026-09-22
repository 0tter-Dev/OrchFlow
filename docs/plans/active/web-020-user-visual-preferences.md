---
id: web-020
status: active
type: feat
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: pending
priority: medium
sequence: 19
depends_on:
  - web-019
authorized_capabilities:
  - capabilities/web-operator-workspace/README.md
  - capabilities/access-control/README.md
decision_records: []
validation:
  - backend-lint
  - backend-type-check
  - backend-test
  - frontend-lint
  - frontend-test
  - frontend-build
  - critical-browser-workflow-test
documentation_updates:
  - docs/capabilities/web-operator-workspace/README.md
  - docs/capabilities/access-control/README.md
  - docs/reference/external-surfaces.md
  - docs/guides/user-guide.md
---

# User Visual Preferences

## Objective

Let each authenticated operator choose a restrained visual presentation that remains accessible, predictable, and independent from lifecycle control.

## Approval

The requesting user explicitly approved activation, implementation, and the persisted/API preference contract on 2026-09-22. The approved fields are `appearance_mode` (`cream-light`, `white-high-contrast`, `gray-dark`, `black-high-contrast`) and `accent_color` (`blue`, `green`, `red`, `yellow`, `orange`, `purple`, `pink`).

## Scope

- extend the established user-preferences workflow with curated appearance modes: cream light, white high-contrast light, gray dark, and black high-contrast dark;
- provide a bounded, accessible accent palette with blue, green, red, yellow, orange, purple, and pink families, each tuned for the selected appearance mode rather than using one raw color across all themes;
- consolidate the existing project display-mode preference into a clear user-facing preferences experience and verify list/table behavior remains useful;
- apply the selected presentation through reusable design tokens, not per-screen color overrides or inline styles;
- persist preferences per authenticated user and preserve the existing rule that preferences cannot affect authorization, ownership, or lifecycle execution;
- define sensible defaults, migration behavior, and fallback rendering for users who have not selected a visual preference.

## Out Of Scope

Arbitrary color pickers, user-uploaded themes, cross-user theme sharing, changing project data, or using visual preferences as a substitute for accessible contrast requirements.

## Acceptance Criteria

- a user can save and restore the supported appearance mode and accent choice independently from other users;
- the selected appearance is applied consistently to the focused shell, project workspace, feedback, and forms;
- list and table project presentations remain selectable through the documented preferences flow;
- every provided color combination meets the project's chosen contrast and focus-state standard;
- backend and frontend contracts, migrations where required, and browser workflows verify persistence and fallback behavior.

## Outcome

Not started.
