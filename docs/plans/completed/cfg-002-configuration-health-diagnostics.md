---
id: cfg-002
status: completed
type: feat
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: pending
priority: high
sequence: 13
depends_on:
  - cfg-001
authorized_capabilities:
  - capabilities/configuration/README.md
  - reference/external-surfaces.md
decision_records: []
validation:
  - backend-lint
  - backend-type-check
  - backend-test
  - cli-api-contract-test
  - windows-setup-check
documentation_updates:
  - docs/capabilities/configuration/README.md
  - docs/guides/user-guide.md
  - docs/guides/installer-and-releases.md
---

# Safe Configuration Health Diagnostics

## Objective

Expose an operator-safe configuration-health summary through the existing backend surfaces and integrate it with — rather than duplicate — the established Windows setup and bootstrap readiness flow.

## Scope

Add a shared application-level diagnosis that groups configuration readiness by concern (runtime paths, database, API/web endpoints, authentication, optional AI). Surface status, missing/invalid keys, remediation text, and source category without exposing secret values. Mirror the intentional diagnostic contract through CLI and API, and let the existing setup/check path invoke or summarize it where useful.

## Out Of Scope

New secret stores, browser-based secret editing, automatic installation of tools, remote host checks, or changes to `.bat` lifecycle authority.

## Approval

The requesting user explicitly approved activation and implementation on 2026-09-19.

## Acceptance Criteria

- CLI and API return the same redacted configuration-health result;
- setup and bootstrap remain the authoritative local prerequisite/readiness workflow;
- a failed configuration reports a next action without leaking values;
- disabled optional AI configuration is reported as intentional rather than failed;
- diagnostics are auditable where an authenticated operator-facing request is made.

## Outcome

Backlog candidate; not started.
