---
id: web-011
status: review
type: feat
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: patch
priority: medium
sequence: 5
depends_on: []
authorized_capabilities:
  - capabilities/web-operator-workspace/README.md
decision_records: []
validation:
  - frontend-lint
  - frontend-test
  - frontend-build
documentation_updates:
  - docs/STATUS.md
  - docs/guides/user-guide.md
---

# Workspace Internationalization

## Objective

Evaluate `i18next` and `react-i18next` to externalize web strings while preserving `pt-BR` and `en-US`.

## Context

The web shell already exposes locale preferences, but scalable translation management needs a single source for strings and tests.

## Decisions

Use the backend-owned user preference as the locale source. Do not introduce automatic browser-language detection that overrides persisted preference.

## Scope

Adopt translation resources, migrate selected workspace strings, and verify locale changes in existing preference flows.

## Out Of Scope

New locales without translated content, backend localization changes, or browser-driven preference replacement.

## Acceptance Criteria

Existing Portuguese and English flows render through translation resources and honor the persisted user choice.

## Validation

Run frontend validation and locale-focused tests.

## Documentation Updates

Update the web capability, user guide, status, and version references.

## Outcome

Implemented in commit `b4573e3` and delivered through [PR #68](https://github.com/0tter-Dev/OrchFlow/pull/68). The approved `i18next` and `react-i18next` dependencies centralize selected `pt-BR` and `en-US` workspace and preference strings while the authenticated persisted locale remains authoritative. Version `0.3.35` advances to `0.3.36`, as expected. Validation passed: 50 API/CLI/documentation contract tests, frontend lint, 50 frontend tests, and frontend build. Awaiting review and merge.
