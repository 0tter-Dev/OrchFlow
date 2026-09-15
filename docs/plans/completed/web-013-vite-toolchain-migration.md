---
id: web-013
status: review
type: chore
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: patch
priority: medium
sequence: 10
depends_on:
  - deps-001
authorized_capabilities:
  - capabilities/web-operator-workspace/README.md
decision_records: []
validation:
  - frontend-lint
  - frontend-test
  - frontend-build
  - local-launcher-smoke-test
documentation_updates:
  - docs/guides/git-and-github-flow.md
---

# Vite Toolchain Migration

## Objective

Evaluate the next Vite toolchain line in a dedicated compatibility change.

## Context

Candidate versions include Vite 8, `@vitejs/plugin-react` 6, Vitest 5, jsdom 30, and TypeScript 7. Their breaking changes can affect build, test, and contributor workflows.

## Decisions

Review supported Node versions, TypeScript configuration, test-environment behavior, plugin compatibility, and release notes before selecting exact versions.

## Scope

Upgrade the selected toolchain group, adjust configuration, and resolve intentional compatibility findings.

## Out Of Scope

UI feature changes, React runtime upgrade, or unrelated dependency maintenance.

## Acceptance Criteria

Development, test, production build, CI, and local launcher flows remain supported and documented.

## Validation

Run frontend validation and a local launcher smoke test.

## Documentation Updates

Update contributor/release guidance and version references only if the supported workflow changes.

## Outcome

User approval recorded on `2026-09-14` to implement the next eligible Roadmap plan. The migration updates the existing Vite toolchain as one compatibility group: Vite `8.3.0`, `@vitejs/plugin-react` `6.1.1`, Vitest `5.0.0`, jsdom `30.0.1`, and TypeScript `6.0.3`. TypeScript 7 was evaluated but deferred because the selected typescript-eslint line does not support it. The release version advances from `0.3.38` to `0.3.39` because the supported contributor toolchain changed. Frontend lint, 51 tests, production build, and local launcher start/status/stop smoke checks passed. Delivered in commits `e84969b` and `2da296d` through PR [#74](https://github.com/0tter-Dev/OrchFlow/pull/74), opened on `2026-09-15`.
