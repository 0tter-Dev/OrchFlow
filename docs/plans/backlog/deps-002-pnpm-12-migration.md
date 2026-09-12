---
id: deps-002
status: backlog
type: chore
requires_pull_request: true
expected_version_impact: patch
authorized_capabilities: []
decision_records: []
validation:
  - frontend-install
  - frontend-lint
  - frontend-test
  - frontend-build
  - windows-launcher-smoke-test
documentation_updates:
  - docs/guides/git-and-github-flow.md
  - docs/guides/installer-and-releases.md
---

# pnpm 12 Migration

## Objective

Evaluate and, if approved, migrate the frontend package manager pin from pnpm 11 to pnpm 12.

## Context

The Windows launcher and setup flow intentionally use `corepack pnpm`, so package-manager changes affect lockfiles, CI, installer behavior, and contributor setup.

## Decisions

Keep pnpm 11 pinned until pnpm 12 passes Corepack, lockfile, CI, Windows launcher, and installer compatibility checks.

## Scope

Update the selected pnpm pin, lockfile if required, CI/setup instructions, and launcher validation only after compatibility is demonstrated.

## Out Of Scope

Node major upgrade, Vite migration, or unrelated web dependency updates.

## Acceptance Criteria

Clean installs and all frontend validations succeed through `corepack pnpm`; setup never depends on global shim writes.

## Validation

Run frontend install/lint/test/build and Windows launcher smoke tests.

## Documentation Updates

Update contributor, installer, status, and version references as required.

## Outcome

Backlog candidate; not started.
