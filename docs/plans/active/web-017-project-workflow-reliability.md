---
id: web-017
status: active
type: fix
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: pending
priority: high
sequence: 16
depends_on:
  - web-016
authorized_capabilities:
  - capabilities/project-registry/README.md
  - capabilities/runtime-inspection/README.md
  - capabilities/web-operator-workspace/README.md
  - capabilities/persistence-and-audit/README.md
decision_records: []
validation:
  - backend-lint
  - backend-type-check
  - backend-test
  - frontend-lint
  - frontend-test
  - frontend-build
  - critical-browser-workflow-test
documentation_updates:
  - docs/capabilities/project-registry/README.md
  - docs/capabilities/runtime-inspection/README.md
  - docs/capabilities/web-operator-workspace/README.md
  - docs/guides/user-guide.md
---

# Project Workflow Reliability

## Objective

Make project registration, runtime loading, and project-contextual history reliable and actionable for a local Windows operator without weakening the authoritative `.bat` lifecycle contract.

## Approval

The requesting user explicitly approved activation and implementation on 2026-09-21.

## Scope

- reproduce and correct the batch runtime-inspection failure so one malformed, unavailable, or otherwise non-inspectable project cannot turn the project workspace load into an unhelpful HTTP 500;
- preserve a useful, per-project inspection result or controlled API error with the underlying safe diagnostic, rather than swallowing the failure;
- investigate and document the compatibility boundary between a menu-driven script such as `VideoHub.bat` and OrchFlow's current non-interactive first-argument invocation model; use representative scripts and tests rather than treating either model as implicitly invalid;
- make registration guidance distinguish a valid batch file, a valid label, a menu-driven entry point, and the separate requirement for a safely automatable command-dispatch path;
- retain the existing canonical `status`, `start`, `stop`, and `restart` contract unless a separately approved product decision establishes a safe, explicit adapter or mapping model for menu-driven scripts;
- correct the contextual history view to match both project target type and project identifier, and make its full-history handoff preserve the selected-project context;
- cover the VideoHub-style script shape: labels exist, but no `%~1` or `%1` dispatch routes execution to them.

## Out Of Scope

Changing lifecycle authority away from Windows `.bat` scripts, executing arbitrary script labels, automatic script rewrites, autonomous remediation, or a broad audit-system redesign.

## Acceptance Criteria

- loading a registry containing an inspection failure remains usable and gives the operator a precise next action;
- an invalid or menu-only lifecycle script is rejected before registration with a localized, actionable explanation of the dispatch requirement;
- a script with explicit first-argument dispatch and matching labels can be registered with the configured mappings;
- the VideoHub-style menu script receives accurate compatibility guidance and cannot be falsely represented as safely automatable; any support beyond guidance follows an explicitly approved contract decision;
- the contextual history never shows same-ID events from another target type and its detailed route remains scoped to the project;
- backend, frontend, and browser coverage includes the failure and successful registration paths.

## Outcome

Not started.
