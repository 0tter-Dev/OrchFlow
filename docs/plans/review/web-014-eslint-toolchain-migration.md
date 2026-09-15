---
id: web-014
status: review
type: chore
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: patch
priority: medium
sequence: 11
depends_on:
  - deps-001
authorized_capabilities:
  - capabilities/web-operator-workspace/README.md
decision_records: []
validation:
  - frontend-lint
  - frontend-test
  - frontend-build
documentation_updates:
  - docs/guides/git-and-github-flow.md
---

# ESLint Toolchain Migration

## Objective

Evaluate ESLint 10, `eslint-plugin-react-hooks` 7, and `globals` 17 as a separate lint compatibility migration.

## Context

Major lint changes can alter flat-config behavior and reveal new findings unrelated to product features.

## Decisions

Confirm flat-config support and classify every new finding as a real correction, an intentional configuration change, or a version incompatibility.

## Scope

Update the lint dependency group and configuration needed for supported rules.

## Out Of Scope

Vite migration, React upgrade, or unrelated UI refactors.

## Acceptance Criteria

Lint rules are explicit, the project is clean, and test/build workflows continue to pass.

## Validation

Run frontend lint, tests, and build.

## Documentation Updates

Update contributor guidance if lint commands, support, or policy changes.

## Outcome

User approval recorded on `2026-09-15` to add ESLint `10.10.0`, eslint-plugin-react-hooks `7.1.1`, and globals `17.12.0`. React Hooks 7 folds React Compiler checks into `rules-of-hooks`; the project explicitly preserves exhaustive dependency checking while deferring the existing Effect Event orchestration refactor outside this migration. Five Effect Event dependency arrays were corrected, and lint, 51 frontend tests, and the production build passed. The release version advances from `0.3.39` to `0.3.40` because the supported lint toolchain changed.
