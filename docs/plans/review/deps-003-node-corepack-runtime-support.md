---
id: deps-003
status: review
type: chore
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: patch
priority: medium
sequence: 9
depends_on:
  - deps-001
authorized_capabilities: []
decision_records: []
validation:
  - windows-setup-check
  - windows-control-smoke-test
  - frontend-build
documentation_updates:
  - docs/guides/installer-and-releases.md
  - docs/guides/git-and-github-flow.md
---

# Node.js And Corepack Runtime Support

## Objective

Define and validate the supported Node.js and Corepack runtime line for OrchFlow.

## Context

Windows setup, process control, CI, bootstrap tooling, and the project-pinned pnpm invocation all rely on Node.js and Corepack behavior.

## Decisions

Evaluate a supported Node LTS line and Corepack version together; coordinate the final choice with any approved pnpm 12 migration.

## Scope

Verify runtime support, launcher behavior, CI configuration, and contributor guidance for the selected line.

## Out Of Scope

Changing product behavior, installing globally managed shims, or bundling a Node runtime with the product.

## Acceptance Criteria

The documented runtime reliably supports `corepack pnpm` installation, development, build, setup, and process-control flows.

## Validation

Run Windows setup/control smoke checks and frontend build with the selected runtime.

## Documentation Updates

Update installer, contributor, status, and version references when the supported runtime changes.

## Outcome

User approval recorded on `2026-09-14` to download and validate the selected Node.js/Corepack tooling and update the supported runtime and CI action as needed. The selected line is Node.js `24` LTS, pinned to `24.21.0` in CI. Corepack remains the Node-bundled package-manager bridge; no separately global Corepack installation or shim is authorized. The release version advances from `0.3.37` to `0.3.38` because the supported Node runtime and CI action changed. Windows setup/control smoke checks, Corepack pnpm install, frontend lint/tests/build, backend lint/type checks, and focused launcher/API contracts passed. The full backend suite was also attempted with a workspace-local temporary directory; CI remains the authoritative complete-suite validation. Delivered in commit `b40feb8` through PR [#73](https://github.com/0tter-Dev/OrchFlow/pull/73), opened on `2026-09-14`.
