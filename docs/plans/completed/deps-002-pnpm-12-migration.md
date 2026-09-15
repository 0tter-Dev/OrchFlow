---
id: deps-002
status: completed
type: chore
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: patch
priority: medium
sequence: 8
depends_on:
  - deps-001
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

User approval was recorded on `2026-09-14`. The project pin now targets pnpm `12.4.1`; pnpm regenerated the lockfile to record the package-manager dependency while application dependency versions remain unchanged. The release version advanced from `0.3.36` to `0.3.37` because the supported package-manager and installation workflow changed.

Validation passed: Corepack resolved pnpm `12.4.1` from `interface/web`; frozen frontend install; frontend lint; 51 frontend tests; production build; 2 Chromium browser workflows; the Windows setup launcher check (including preserved `.env` files and Corepack-managed installation); Ruff; mypy; 152 backend tests; and 19 version, documentation, and launcher contract tests. Delivered in commits `f294a53` and `dad5f45` through [PR #72](https://github.com/0tter-Dev/OrchFlow/pull/72), merged on `2026-09-14`.
