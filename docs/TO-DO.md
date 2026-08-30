# TO-DO

## Purpose

This document tracks the next planned steps for OrchFlow after the initial documentation foundation.

## Current Implementation Sequence

The completed implementation sequence now covers the backend bootstrap foundation, configuration plus persistence bootstrap, access-control foundation, project-registry foundation, lifecycle-orchestration foundation, runtime-inspection milestone, web-bootstrap milestone, the first practical web integration flow, real project onboarding hardening for existing `.bat` scripts, the first web project registration flow, lifecycle history plus audit visibility, admin plus project ownership management, runtime inspection refinement, CI plus contract hardening, documentation/versioning governance for pull requests, the LiteLLM dependency plus disabled-by-default AI configuration baseline, the first domain-level ideal lifecycle function model, automatic lifecycle script detection with derived configuration health, API/CLI workflows for manual lifecycle mapping plus explicit `unconfigured` decisions, explicit project reload for one project or multiple projects in sequence, lifecycle execution gating for partial or blocked configurations, web lifecycle configuration indicators plus mapping controls, the authenticated AI assistance boundary with a LiteLLM gateway status client, LiteLLM gateway health plus model discovery through API and CLI, authorized project context manifests, and reviewable AI analysis proposals without file writes.

`v0.3.3` consolidates the first usable backend, `CLI`, `API`, and `web` baseline for authenticated operation of registered projects, including project visibility, lifecycle execution, refined runtime inspection, admin audit visibility, user and ownership management, CI validation, lifecycle controls backed by Windows `.bat` scripts, preferred-action detection, project configuration health, reviewable manual lifecycle configuration decisions, explicit reload after local `.bat` changes, configured-action execution enforcement, web mapping controls, authenticated AI assistance status, LiteLLM gateway health, LiteLLM model discovery, authorized context manifests, and reviewable AI analysis proposals.

The current frontend package manager decision is `pnpm`.

Implemented planning items should be removed from this document as work progresses so it remains focused on what comes next.

## Next Implementation Roadmap

The next implementation sequence should build on reload-aware and execution-gated lifecycle configuration before deeper LiteLLM-backed AI assistance. The ideal model now gives OrchFlow a stable reference for AI-assisted `.bat` improvement.

1. **Review, Validation, And Approval Workflow**
   Add proposal review operations through `API`, `CLI`, and then `web`. Validate proposed scripts against the lifecycle script template, first-argument dispatch expectations, required canonical actions, and mapping consistency. Rejections and approvals must be audited.

2. **Approved `.bat` File Generation And Mapping Persistence**
   After review is implemented, allow approved proposals to create or overwrite lifecycle `.bat` files and persist approved action mappings. File writes must require explicit confirmation, preserve audit details, and reuse the existing project registry validation path before the project becomes operational.

3. **Project Registry And Mapping Management Completion**
   Add non-AI project update workflows for editing project metadata, lifecycle script path, action mappings, and owners while preserving auditability and access rules. This closes the remaining registry gap toward a complete managed-project lifecycle.

4. **Runtime Inspection And History Maturity**
   Improve runtime inspection for projects without `APP_PORT`, add clearer diagnostics for timeout and unsupported states, and evaluate whether runtime snapshots should be persisted for project history. Keep deep observability out of scope unless a later product decision changes it.

5. **Admin, Audit, And Permission Refinement**
    Add audit filtering by project, actor, action, and time window; refine permission semantics beyond role plus ownership when needed; and improve admin troubleshooting workflows across `CLI`, `API`, and `web`.

6. **Web Operator Experience Completion**
    Expand the web workspace with project editing, AI proposal review, richer error states, guided onboarding, audit filtering, and clearer runtime diagnostics after the backend contracts are stable.

7. **CI, Contracts, And Release Discipline**
    Add contract tests for AI assistance routes, tests for version bump discipline where practical, deeper migration checks when justified, and eventual release automation for tag validation and release notes.

## Cross-Cutting Rules

- expand the mirrored operator workflow in `CLI`, `API`, and `web` together whenever a new user-facing capability is intentionally introduced
- keep Windows `.bat` lifecycle scripts as the authoritative operational contract for managed projects in `v0.3.3`
- implement each roadmap step as a coherent Conventional Commit change unit and document the semantic version decision in the pull request
- evaluate version impact before starting a roadmap step and confirm it after the diff is complete, especially for AI assistance milestones such as the `AI Agent Adapter` and `LiteLLM` integration
- avoid container orchestration, remote orchestration, and speculative support layers unless a later approved requirement changes the product scope
- update `docs/STATUS.md`, `docs/USER-GUIDE.md`, and authorized scope-relevant context documentation whenever a roadmap milestone changes implemented behavior
- revisit future `mobile` and `desktop` planning only after the API and web flows are stable
