---
id: docs-001
status: completed
type: docs
requires_pull_request: true
expected_version_impact: patch
authorized_capabilities:
  - capabilities/access-control/README.md
  - capabilities/ai-assistance/README.md
  - capabilities/configuration/README.md
  - capabilities/lifecycle-management/README.md
  - capabilities/lifecycle-management/adapter-contract.md
  - capabilities/lifecycle-management/script-contract.md
  - capabilities/project-registry/README.md
  - capabilities/runtime-inspection/README.md
  - capabilities/persistence-and-audit/README.md
  - capabilities/web-operator-workspace/README.md
decision_records:
  - decisions/ADR-0001-local-first-bat-lifecycle-contract.md
  - decisions/ADR-0002-lifecycle-function-configuration-model.md
  - decisions/ADR-0003-litellm-through-orchflow-ai-adapter.md
  - decisions/ADR-0004-local-sqlite-and-ownership-authorization.md
validation:
  - documentation-structure-test
  - markdown-link-check
documentation_updates:
  - README.md
  - AGENTS.md
---

# Documentation Governance Modularization

## Objective

Adopt the capability, reference, guide, ADR, and plan documentation model.

## Context

Explicitly approved by the requesting user on 2026-09-10.

## Decisions

Use English technical names, `active/backlog/completed` plans, and limited active-plan context authorization.

## Scope

Move current documentation into the new taxonomy, create the governance documents and ADRs, update navigation and agent policy, and add structure validation.

## Out Of Scope

No product API, runtime, or lifecycle behavior changes.

## Acceptance Criteria

The documented taxonomy exists, all links resolve, active-plan authorization is enforced in policy, and the validation test passes.

## Validation

Run the documentation structure test, link check, backend validation, and frontend validation.

## Documentation Updates

All root documentation, moved documents, links, templates, and version references are updated.

## Outcome

Implemented the modular documentation topology, navigation, ADR baseline, limited plan-context authorization policy, and repository contract validation. Validation passed with `uv run ruff check .`, `uv run mypy src`, `uv run pytest --basetemp runtime/pytest-validation`, `pnpm lint`, `pnpm test -- --run`, and `pnpm build`. The delivery commit and pull request are recorded by the branch and review workflow.
