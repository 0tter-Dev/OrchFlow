# Feature Status

## Purpose

This document tracks the current implementation state of major OrchFlow capabilities.

## Legend

- `planned`: defined in documentation but not started
- `in_progress`: currently being implemented
- `implemented`: available in the product
- `review_needed`: present but requires design or behavior review

## Current Project Stage

OrchFlow is currently in the `v0.3.15` implementation stage as of `2026-09-01`.

## Feature Table

| Feature | Purpose | Status | Notes |
| --- | --- | --- | --- |
| Project architecture | Define scope, rules, constraints, and goals | implemented | Initial documentation baseline created |
| Development guide | Define engineering and architectural discipline | implemented | Initial standards established |
| User guide | Explain the intended usage flow | implemented | First example workflow documented |
| To-do roadmap | Track next planned project steps | implemented | Current implementation roadmap documented and kept focused on upcoming work |
| Agent rules | Constrain AI-assisted project changes | implemented | `AGENTS.md` created |
| Python project metadata | Define the backend package and toolchain baseline | implemented | `uv`, `pyproject.toml`, and the LiteLLM dependency baseline are initialized |
| Frontend package manager decision | Define the JavaScript package manager baseline for the web client | implemented | `pnpm` selected for the `interface/web` direction |
| Repository standards | Define ignore rules, line endings, editor behavior, and license | implemented | Git foundation files created |
| Configuration contract | Define runtime configuration and `.env` direction | in_progress | Validated settings loading, path normalization, and disabled-by-default LiteLLM AI settings are implemented; further feature-specific config still pending |
| Access control | Authenticate users and enforce permissions | implemented | Bootstrap admin creation, JWT login, current-user resolution, admin listing, user role/activation updates, last-active-admin protection, and audit logging are implemented |
| Project registry | Register and persist project definitions | implemented | Existing `.bat` registration, project metadata and script-path updates, ownership persistence and management, normalized action mappings, first-argument dispatch validation, preferred identifier auto-detection, partial registration, manual lifecycle mapping, explicit unconfigured decisions, explicit reload, and derived configuration health are implemented |
| Ideal lifecycle function model | Define expected `.bat` functions and project configuration health | in_progress | Fixed ideal functions, function states, preferred mapping detection, manual mapping, explicit unconfigured decisions, reload-aware remapping, configured-action execution gating, and derived complete/partial/blocked health are implemented; warning UI and AI-assisted improvement remain upcoming |
| Project adapter | Connect OrchFlow to managed projects through a generic adapter boundary | implemented | Windows `.bat` command-dispatch adapter with canonical action mapping resolution is implemented |
| Lifecycle script template | Define the standard `.bat` contract used by managed projects | implemented | Includes minimum actions and a concrete reference-based example |
| Lifecycle orchestration | Run `status`, `start`, `stop`, `restart` | implemented | Configured lifecycle actions execute through API and CLI; undefined, unconfigured, or fully blocked configurations are rejected with auditable operator-facing feedback |
| Runtime inspection | Inspect ports, PID, CPU, memory, uptime | implemented | Windows-local inspection with port, APP_URL-only reachability fallback, URL timeout diagnostics, unsupported no-hint diagnostics, inspection timestamp, PID, uptime, CPU, and memory summaries is exposed in API, CLI, and web |
| AI assistance adapter with LiteLLM gateway | Analyze project folders and help generate `.bat` scripts | in_progress | The authenticated OrchFlow-owned status, LiteLLM gateway health, model discovery, authorized context manifest, reviewable analysis proposal, proposal review, confirmed proposal application, and web review/application UI boundaries are implemented |
| CLI surface | Expose orchestration through terminal commands | in_progress | Authentication, project registry, lifecycle execution, runtime inspection, filtered admin audit history, user management, and owner management are mirrored; broader operator workflows still pending |
| API surface | Expose orchestration through HTTP endpoints | in_progress | Authentication, project registry, lifecycle execution, runtime inspection, filtered admin audit history, user management, and owner management are mirrored; broader operator workflows still pending |
| Interface layer | Visualize and control projects across client platforms | in_progress | `interface/web` includes authenticated session loading, project registration, first-project and selected-project onboarding guidance, project visibility, project editing, runtime inspection, guided operational readiness, richer API error notices, configured lifecycle controls, lifecycle configuration indicators, manual mapping controls, project reload, filtered admin audit history, user management, owner management, AI proposal review/application, and a shared API client boundary |
| Persistence and audit | Store users, projects, permissions, events | implemented | SQLAlchemy engine/session bootstrap, Alembic migrations, users, audit events, projects, ownership, lifecycle action mappings, AI context manifests, AI analysis proposals, proposal review decisions, proposal application records, and admin history visibility are implemented |
| DevOps and CI | Enforce repository quality and automation | implemented | Git and GitHub flow documented, including PR version decisions, human-driven and agent-driven PR modes; PR and issue templates, migration validation, focused AI API contract tests, API contract coverage, critical web-flow tests, and full project validation checks are in place |

## Implementation Notes

- The initial project planning, documentation baseline, and repository skeleton were completed before the current implementation stage.
- The consolidated documentation model and Git plus GitHub workflow foundation were completed before the current implementation stage.
- The project is now operating in `v0.3.15`, which consolidates the first real backend and web implementation milestones, runtime inspection refinement, APP_URL-only reachability fallback, clearer unsupported and timeout diagnostics, filtered admin audit history by actor, action, project, and time window, admin and ownership management, LiteLLM dependency onboarding, documentation/versioning governance, roadmap planning at one-PR granularity, CI plus contract hardening, focused AI API contract tests, the first ideal lifecycle function domain model, automatic lifecycle configuration health, manual lifecycle configuration decisions, explicit project reload, configured-action lifecycle execution gating, non-AI project update workflows, web project editing, web lifecycle configuration controls, guided operational readiness, first-project and selected-project onboarding guidance, richer API error notices, authenticated AI assistance status, gateway health, model discovery, authorized context manifests, reviewable analysis proposals, proposal review decisions, confirmed proposal application, web AI proposal review/application, and pytest cache relocation to `runtime/pytest-cache` on `main`.
- The initial backend bootstrap now exists with executable API and CLI entrypoints plus smoke tests.
- Configuration loading, runtime path normalization, disabled-by-default LiteLLM AI settings, SQLAlchemy bootstrap, and Alembic migrations are available as part of the current baseline.
- API and CLI should keep evolving as mirrored external surfaces whenever a capability is intentionally exposed to operators.
- Access control is now implemented at the foundation level with mirrored registration, login, current-user, admin listing, and admin user update flows in API and CLI.
- Project registry is now implemented for existing `.bat` onboarding, with ownership persistence and management, auditable project metadata updates, lifecycle script-path updates, lifecycle action mappings, registration-time validation for first-argument dispatch compatibility, automatic preferred-identifier detection, partial project registration, manual lifecycle configuration updates, and explicit project reload exposed through API and CLI contracts.
- The ideal lifecycle function model now defines the initial fixed expected functions, preferred script identifiers, function configuration states, and derived project configuration health in code. Project responses now expose complete, partial, or blocked health and function-level configuration states, including explicit `unconfigured` decisions. Reload can reread a script, preserve valid user decisions, refresh imported mappings, show changed actions, and audit the before/after health. Lifecycle execution now rejects undefined, explicitly unconfigured, or fully blocked actions before adapter execution. Warning UI and AI-assisted improvements remain upcoming.
- Lifecycle orchestration is now implemented with the first Windows batch execution flow using command-dispatch by argument and mirrored lifecycle actions in API and CLI.
- Runtime inspection is now implemented with a Windows-local baseline that extracts script hints, inspects listening ports and process metadata, uses `APP_URL` reachability when `APP_PORT` is absent, reports unsupported state when no runtime hints exist, explains URL timeout and reachability failures, and mirrors the capability in API, CLI, and web. Runtime snapshot persistence was evaluated for this milestone and remains deferred until project history needs more than audit events and on-demand inspection.
- AI-assisted onboarding is now being implemented around a LiteLLM-backed gateway rather than direct provider-specific integration. Status, gateway health, model discovery, authorized context manifest, analysis proposal, proposal review, and approved application boundaries are available through `GET /ai/status`, `GET /ai/gateway/health`, `GET /ai/models`, `POST /ai/context-manifests`, `GET /ai/context-manifests/{manifest_id}`, `POST /ai/analysis-proposals`, `GET /ai/analysis-proposals/{proposal_id}`, `POST /ai/analysis-proposals/{proposal_id}/review`, `POST /ai/analysis-proposals/{proposal_id}/apply`, `orchflow ai status`, `orchflow ai health`, `orchflow ai models`, `orchflow ai manifest-create`, `orchflow ai manifest-show`, `orchflow ai proposal-create`, `orchflow ai proposal-show`, `orchflow ai proposal-review`, and `orchflow ai proposal-apply`; the authenticated web workspace now consumes the same status, manifest, proposal, review, and apply contracts. They require an authenticated user, record audit events, and keep LiteLLM access behind the OrchFlow adapter. Proposal creation may send only manifest-approved project context to the selected model and persists structured proposal data for review without writing `.bat` files. Proposal approval validates first-argument dispatch, required canonical actions, and mapping consistency before recording the approval. Proposal application requires explicit file-write and mapping-persistence confirmations, writes or overwrites the lifecycle `.bat`, expands effective canonical mappings where ideal labels are used, persists them as `ai_approved`, and records a dedicated application record plus audit event.
- Admin audit history visibility is now implemented through a shared application service and exposed as `GET /audit/events`, `orchflow audit events`, and the web audit panel for recent operational events, with filters for actor, action, project, and time window.
- Admin and ownership management is now implemented through user role/activation updates, last-active-admin protection, project owner add/remove operations, and the first web admin management panel.
- The first practical web client flow now exists in `interface/web`, covering sign-in, existing `.bat` project registration, first-project and selected-project onboarding guidance, project listing, project details, project metadata and path editing, runtime inspection visibility, operational readiness guidance, richer API and validation error notices, configured lifecycle controls, lifecycle configuration health, manual mapping, reload, filtered admin audit history, user management, and owner management against the stabilized API contracts.
- The web client now uses a local proxy-friendly API base URL contract so frontend development can stay aligned with the backend surface without introducing special backend-only web behavior.
- The Git and GitHub maintenance flow is now documented.
- The Git and GitHub flow now documents both human-driven and agent-driven pull request authorship, while preserving human review and merge authority on protected branches.
- Pull request descriptions now explicitly use `.github/PULL_REQUEST_TEMPLATE.md` as the standard structure for reviewer-facing summaries, validation notes, version decisions, and documentation checklists.
- Pull request and issue templates plus CI workflow coverage for backend and frontend validation have been added locally.
- The `OrchFlow - Full Validation` workflow now runs backend quality checks, Alembic migration validation, backend API contract tests through the test suite, frontend lint, frontend tests, and frontend build verification.
- AI API contract coverage now locks authentication requirements, FastAPI validation behavior, safe gateway response fields, manifest/proposal/review/application response shapes, and explicit proposal application confirmations.
- API contract coverage now locks the currently exposed authenticated operator routes and key response fields for runtime diagnostics and project ownership metadata.
- Critical web-flow coverage now includes existing `.bat` project registration behavior and selecting visible registered projects from the operator list.
- The frontend package manager direction is now defined as `pnpm`.
- The repository workflow now supports both maintainer-authored and agent-authored pull requests with a dedicated repository identity and human-controlled review on `main`.
- Any implementation work should update this file as features move from `planned` to later states.
