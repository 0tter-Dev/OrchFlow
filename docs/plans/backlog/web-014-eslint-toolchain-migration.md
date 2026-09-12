---
id: web-014
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

Backlog candidate; not started.
