# TO-DO

## Purpose

This document tracks the next planned steps for OrchFlow after the initial documentation foundation.

## Current Implementation Sequence

The completed implementation sequence now covers the backend bootstrap foundation, configuration plus persistence bootstrap, access-control foundation, project-registry foundation, lifecycle-orchestration foundation, runtime-inspection milestone, web-bootstrap milestone, the first practical web integration flow, real project onboarding hardening for existing `.bat` scripts, the first web project registration flow, lifecycle history plus audit visibility, admin plus project ownership management, runtime inspection refinement, CI plus contract hardening, documentation/versioning governance for pull requests, the LiteLLM dependency plus disabled-by-default AI configuration baseline, the first domain-level ideal lifecycle function model, and automatic lifecycle script detection with derived configuration health.

`v0.2.11` consolidates the first usable backend, `CLI`, `API`, and `web` baseline for authenticated operation of registered projects, including project visibility, lifecycle execution, refined runtime inspection, admin audit visibility, user and ownership management, CI validation, and lifecycle controls backed by Windows `.bat` scripts with a shared ideal lifecycle function reference, preferred-action detection, and project configuration health.

The current frontend package manager decision is `pnpm`.

Implemented planning items should be removed from this document as work progresses so it remains focused on what comes next.

## Next Implementation Roadmap

The next implementation sequence should build on automatic lifecycle script detection before deeper LiteLLM-backed AI assistance. The ideal model now gives OrchFlow a stable reference for manual configuration, project reload, warnings, blocking rules, and later AI-assisted `.bat` improvement.

1. **Manual Mapping And Explicit Unconfigured Decisions**
   Add API and CLI workflows for users to map ideal lifecycle functions to discovered or manually entered script identifiers, or explicitly mark functions as unconfigured. Persist these decisions with audit metadata and keep configured actions validated against first-argument dispatch support.

2. **Project Reload Workflow**
   Add explicit reload for one project and for multiple projects in sequence. Reload should reread lifecycle scripts, refresh automatic detection, preserve user decisions where appropriate, surface changed mapping guidance, and audit changes that affect controllability or warnings.

3. **Lifecycle Execution With Partial Configuration**
   Update lifecycle orchestration and adapters so only configured lifecycle functions can be executed. Undefined or unconfigured actions should return clear operator-facing feedback. Projects with partial configuration should remain visible and usable; projects with no configured action should be blocked from lifecycle operation.

4. **Web Configuration Indicators And Mapping Flow**
   Expose configuration health in the web interface. Partial projects should show a warning and provide access to mapping details, manual configuration, and future AI-assisted improvement. Blocked projects should show an error explaining that at least one lifecycle function must be configured before operation.

5. **AI Assistance Boundary And LiteLLM Gateway Client**
   Define an OrchFlow-owned AI assistance application boundary and a LiteLLM gateway infrastructure client behind it. Validate the boundary through tests before exposing project analysis.

6. **LiteLLM Gateway Health And Model Discovery**
   Add backend use cases to verify the configured LiteLLM gateway and list configured models or agents when supported. Mirror this through `CLI` and `API`, and expose read-only status in `web` only after API contracts are stable. This milestone must not send project files to any model.

7. **Authorized Project Context Manifest**
   Implement an allowed-context manifest for AI analysis sessions. The manifest should identify the selected project folder, included files, excluded paths, ignored/generated artifacts, secret filtering rules, size limits, selected model, requesting user, and intended operation. Persist and audit authorization metadata without storing secrets.

8. **Analysis Proposal Without File Writes**
   Implement the first review-driven analysis flow. The model may receive only approved context and should return structured proposals describing lifecycle strategy, expected runtime hints, candidate `.bat` content, and possible action mappings. Store proposal metadata and audit the request, but do not write files or persist mappings yet.

9. **Review, Validation, And Approval Workflow**
   Add proposal review operations through `API`, `CLI`, and then `web`. Validate proposed scripts against the lifecycle script template, first-argument dispatch expectations, required canonical actions, and mapping consistency. Rejections and approvals must be audited.

10. **Approved `.bat` File Generation And Mapping Persistence**
   After review is implemented, allow approved proposals to create or overwrite lifecycle `.bat` files and persist approved action mappings. File writes must require explicit confirmation, preserve audit details, and reuse the existing project registry validation path before the project becomes operational.

11. **Project Registry And Mapping Management Completion**
   Add non-AI project update workflows for editing project metadata, lifecycle script path, action mappings, and owners while preserving auditability and access rules. This closes the remaining registry gap toward a complete managed-project lifecycle.

12. **Runtime Inspection And History Maturity**
   Improve runtime inspection for projects without `APP_PORT`, add clearer diagnostics for timeout and unsupported states, and evaluate whether runtime snapshots should be persisted for project history. Keep deep observability out of scope unless a later product decision changes it.

13. **Admin, Audit, And Permission Refinement**
    Add audit filtering by project, actor, action, and time window; refine permission semantics beyond role plus ownership when needed; and improve admin troubleshooting workflows across `CLI`, `API`, and `web`.

14. **Web Operator Experience Completion**
    Expand the web workspace with project editing, AI proposal review, richer error states, guided onboarding, audit filtering, and clearer runtime diagnostics after the backend contracts are stable.

15. **CI, Contracts, And Release Discipline**
    Add contract tests for AI assistance routes, tests for version bump discipline where practical, deeper migration checks when justified, and eventual release automation for tag validation and release notes.

## Cross-Cutting Rules

- expand the mirrored operator workflow in `CLI`, `API`, and `web` together whenever a new user-facing capability is intentionally introduced
- keep Windows `.bat` lifecycle scripts as the authoritative operational contract for managed projects in `v0.2.11`
- avoid container orchestration, remote orchestration, and speculative support layers unless a later approved requirement changes the product scope
- update `docs/STATUS.md`, `docs/USER-GUIDE.md`, and authorized scope-relevant context documentation whenever a roadmap milestone changes implemented behavior
- revisit future `mobile` and `desktop` planning only after the API and web flows are stable
