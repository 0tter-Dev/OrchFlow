# TO-DO

## Purpose

This document tracks the next planned steps for OrchFlow after the initial documentation foundation.

## Current Implementation Sequence

The completed implementation sequence now covers the backend bootstrap foundation, configuration plus persistence bootstrap, access-control foundation, project-registry foundation, lifecycle-orchestration foundation, runtime-inspection milestone, web-bootstrap milestone, the first practical web integration flow, real project onboarding hardening for existing `.bat` scripts, the first web project registration flow, lifecycle history plus audit visibility, admin plus project ownership management, runtime inspection refinement, CI plus contract hardening, documentation/versioning governance for pull requests, the LiteLLM dependency plus disabled-by-default AI configuration baseline, the first domain-level ideal lifecycle function model, automatic lifecycle script detection with derived configuration health, API/CLI workflows for manual lifecycle mapping plus explicit `unconfigured` decisions, explicit project reload for one project or multiple projects in sequence, lifecycle execution gating for partial or blocked configurations, web lifecycle configuration indicators plus mapping controls, and the authenticated AI assistance boundary with a LiteLLM gateway status client.

`v0.2.16` consolidates the first usable backend, `CLI`, `API`, and `web` baseline for authenticated operation of registered projects, including project visibility, lifecycle execution, refined runtime inspection, admin audit visibility, user and ownership management, CI validation, lifecycle controls backed by Windows `.bat` scripts, preferred-action detection, project configuration health, reviewable manual lifecycle configuration decisions, explicit reload after local `.bat` changes, configured-action execution enforcement, web mapping controls, and the first authenticated AI assistance status boundary.

The current frontend package manager decision is `pnpm`.

Implemented planning items should be removed from this document as work progresses so it remains focused on what comes next.

## Next Implementation Roadmap

The next implementation sequence should build on reload-aware and execution-gated lifecycle configuration before deeper LiteLLM-backed AI assistance. The ideal model now gives OrchFlow a stable reference for AI-assisted `.bat` improvement.

1. **LiteLLM Gateway Health And Model Discovery**
   Add backend use cases to verify the configured LiteLLM gateway and list configured models or agents when supported. Mirror this through `CLI` and `API`, and expose read-only status in `web` only after API contracts are stable. This milestone must not send project files to any model.

2. **Authorized Project Context Manifest**
   Implement an allowed-context manifest for AI analysis sessions. The manifest should identify the selected project folder, included files, excluded paths, ignored/generated artifacts, secret filtering rules, size limits, selected model, requesting user, and intended operation. Persist and audit authorization metadata without storing secrets.

3. **Analysis Proposal Without File Writes**
   Implement the first review-driven analysis flow. The model may receive only approved context and should return structured proposals describing lifecycle strategy, expected runtime hints, candidate `.bat` content, and possible action mappings. Store proposal metadata and audit the request, but do not write files or persist mappings yet.

4. **Review, Validation, And Approval Workflow**
   Add proposal review operations through `API`, `CLI`, and then `web`. Validate proposed scripts against the lifecycle script template, first-argument dispatch expectations, required canonical actions, and mapping consistency. Rejections and approvals must be audited.

5. **Approved `.bat` File Generation And Mapping Persistence**
   After review is implemented, allow approved proposals to create or overwrite lifecycle `.bat` files and persist approved action mappings. File writes must require explicit confirmation, preserve audit details, and reuse the existing project registry validation path before the project becomes operational.

6. **Project Registry And Mapping Management Completion**
   Add non-AI project update workflows for editing project metadata, lifecycle script path, action mappings, and owners while preserving auditability and access rules. This closes the remaining registry gap toward a complete managed-project lifecycle.

7. **Runtime Inspection And History Maturity**
   Improve runtime inspection for projects without `APP_PORT`, add clearer diagnostics for timeout and unsupported states, and evaluate whether runtime snapshots should be persisted for project history. Keep deep observability out of scope unless a later product decision changes it.

8. **Admin, Audit, And Permission Refinement**
    Add audit filtering by project, actor, action, and time window; refine permission semantics beyond role plus ownership when needed; and improve admin troubleshooting workflows across `CLI`, `API`, and `web`.

9. **Web Operator Experience Completion**
    Expand the web workspace with project editing, AI proposal review, richer error states, guided onboarding, audit filtering, and clearer runtime diagnostics after the backend contracts are stable.

10. **CI, Contracts, And Release Discipline**
    Add contract tests for AI assistance routes, tests for version bump discipline where practical, deeper migration checks when justified, and eventual release automation for tag validation and release notes.

## Cross-Cutting Rules

- expand the mirrored operator workflow in `CLI`, `API`, and `web` together whenever a new user-facing capability is intentionally introduced
- keep Windows `.bat` lifecycle scripts as the authoritative operational contract for managed projects in `v0.2.16`
- avoid container orchestration, remote orchestration, and speculative support layers unless a later approved requirement changes the product scope
- update `docs/STATUS.md`, `docs/USER-GUIDE.md`, and authorized scope-relevant context documentation whenever a roadmap milestone changes implemented behavior
- revisit future `mobile` and `desktop` planning only after the API and web flows are stable
