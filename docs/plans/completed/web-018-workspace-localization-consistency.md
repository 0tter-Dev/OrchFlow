---
id: web-018
status: completed
type: fix
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: patch
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

The requesting user explicitly approved activation and implementation on 2026-09-21.

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

Implemented in [PR #85](https://github.com/0tter-Dev/OrchFlow/pull/85) with delivery
commit `42f007f`, followed by version-consistency fix `c49f3b1`, and merged as
`014566b` on 2026-09-22.

- Expected and actual version impact: `patch`, advancing `0.3.44` to `0.3.45`.
- Centralized `pt-BR` and `en-US` copy now covers the authenticated workspace
  surfaces delivered by this plan, with locale-aware health and audit timestamps.
- Validation passed: 45 backend contract tests, 55 frontend tests, frontend lint,
  production build, and three critical Playwright workflows.
