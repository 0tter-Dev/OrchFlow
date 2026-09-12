---
id: deps-003
status: backlog
type: chore
requires_pull_request: true
expected_version_impact: patch
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

Backlog candidate; not started.
