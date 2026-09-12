---
id: web-013
status: backlog
type: chore
requires_pull_request: true
expected_version_impact: none
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

Backlog candidate; not started.
