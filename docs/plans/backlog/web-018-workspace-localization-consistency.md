---
id: web-018
status: backlog
type: fix
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: pending
priority: high
sequence: 17
depends_on:
  - web-017
authorized_capabilities:
  - capabilities/web-operator-workspace/README.md
  - capabilities/access-control/README.md
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

# Workspace Localization Consistency

## Objective

Make every operator-facing web workspace message consistently follow the authenticated user's selected locale, including empty states, actions, feedback, and safe error presentation.

## Approval

Awaiting explicit user approval to move to `active`.

## Scope

- inventory all user-visible strings in the authenticated workspace and place them behind the established localization boundary;
- complete Portuguese and English coverage for navigation, project registration, lifecycle feedback, activity, profile, administration, preferences, and system state;
- ensure locale changes apply coherently to labels, status values, dates, empty states, validation feedback, and client-owned error wrappers;
- preserve safe server diagnostics while translating the surrounding explanation and recovery action;
- remove the current mixed-language experience without duplicating translation logic inside feature components.

## Out Of Scope

Adding new locales beyond the existing supported set, translating arbitrary project content, changing authentication semantics, or changing backend business errors solely for cosmetic wording.

## Future Consideration

Spanish is a prospective additional locale. This plan must keep translations and locale selection extensible enough to support a later Spanish delivery, but does not add Spanish strings or expose it as a selectable locale.

## Acceptance Criteria

- switching the saved locale yields a coherent workspace with no unintended English or Portuguese UI strings;
- localized validation and operational feedback retain their accessibility roles and actionable detail;
- dates, counts, and status wording honor the selected locale where supported by the client;
- automated coverage verifies both locale paths for representative project and settings workflows.

## Outcome

Not started.
