# TO-DO

## Purpose

This document tracks the next planned steps for OrchFlow after the initial documentation foundation.

## Current Implementation Sequence

The completed implementation sequence now covers the backend bootstrap foundation, configuration plus persistence bootstrap, access-control foundation, project-registry foundation, lifecycle-orchestration foundation, runtime-inspection milestone, web-bootstrap milestone, the first practical web integration flow, real project onboarding hardening for existing `.bat` scripts, the first web project registration flow, lifecycle history plus audit visibility, admin plus project ownership management, runtime inspection refinement, CI plus contract hardening, documentation/versioning governance for pull requests, the LiteLLM dependency plus disabled-by-default AI configuration baseline, the first domain-level ideal lifecycle function model, automatic lifecycle script detection with derived configuration health, API/CLI workflows for manual lifecycle mapping plus explicit `unconfigured` decisions, explicit project reload for one project or multiple projects in sequence, lifecycle execution gating for partial or blocked configurations, web lifecycle configuration indicators plus mapping controls, the authenticated AI assistance boundary with a LiteLLM gateway status client, LiteLLM gateway health plus model discovery through API and CLI, authorized project context manifests, reviewable AI analysis proposals without file writes, API/CLI proposal review decisions with validation, pytest cache relocation to `runtime/pytest-cache`, explicit approved proposal application that writes lifecycle `.bat` files and persists effective `ai_approved` mappings only after separate user confirmations, non-AI API/CLI project update workflows for metadata, lifecycle script paths, and lifecycle mappings, runtime inspection maturity for `APP_URL`-only projects, unsupported no-hint diagnostics, URL timeout explanations, filtered admin audit history across API, CLI, and web, web project editing for metadata plus lifecycle paths, web AI proposal review/application, web guided operational readiness for lifecycle and runtime diagnostics, richer web API/validation error states, roadmap governance that treats each planned step as one pull-request-sized change, web guided onboarding polish for first-project and selected-project states, focused AI API contract tests, version consistency contract tests, hardened Alembic revision graph plus schema drift tests, manual release tag validation plus release-note artifact generation, split Windows setup and control launchers, PID-based local API and web process control, backend-owned user web preferences for locale, project display mode, and status refresh interval across API, CLI, and web, authorized batch runtime inspection for visible projects across API, CLI, and web, the compact web operator workspace redesign, the project unlink workflow across API, CLI, and web, the focused unauthenticated web login plus account-creation flow, and stabilized authenticated web health refresh that keeps the latest known API snapshot visible during refresh attempts and transient failures.

`v0.3.27` consolidates the first usable backend, `CLI`, `API`, and `web` baseline for authenticated operation of registered projects, including project visibility, project metadata/script update workflows, project unlink without local file deletion, web project editing, lifecycle execution, refined runtime inspection for `APP_URL`-only projects and clearer timeout/unsupported diagnostics, authorized multi-project runtime inspection, a compact daily operator workspace, stable authenticated health refresh that preserves the latest known API snapshot through refresh loading and transient failures, a focused unauthenticated web authentication surface with `Login` and role-neutral `Create account`, simple `pt-BR` and `en-US` shell text dictionaries, guided operational readiness, first-project and selected-project onboarding guidance, richer API and validation error notices, roadmap planning at one-PR granularity, focused AI API contract tests, version consistency contract tests, hardened Alembic revision graph plus schema drift tests, manual release tag validation plus release-note artifact generation, split Windows setup and control launchers, PID-based local API and web process control, backend-owned user web preferences, filtered admin audit visibility, user and ownership management, CI validation, lifecycle controls backed by Windows `.bat` scripts, preferred-action detection, project configuration health, reviewable manual lifecycle configuration decisions, explicit reload after local `.bat` changes, configured-action execution enforcement, web mapping controls, authenticated AI assistance status, LiteLLM gateway health, LiteLLM model discovery, authorized context manifests, reviewable AI analysis proposals, proposal review decisions, confirmed application of approved proposals, and web AI proposal review/application.

The current frontend package manager decision is `pnpm`.

Implemented planning items should be removed from this document as work progresses so it remains focused on what comes next. Roadmap items should be granular by default: each numbered step should describe one coherent pull-request-sized change, not a broad workstream that requires multiple pull requests to finish. When a planned workstream is still too broad, split it into sequential steps before implementation starts.

## Next Implementation Roadmap

1. `feat(web-ui): add accessible UI primitives and icons`

   Objective: establish a consistent, accessible UI interaction foundation for future web operator controls without turning the interface into a heavy design-system rewrite.

   Main scope: add `lucide-react` for consistent operational icons and Radix Primitives for accessible dialogs, alert dialogs, toasts, dropdowns, tabs, tooltips, or popovers as needed by actual web flows; introduce only small shared wrappers when they serve current screens; keep styling owned by OrchFlow CSS; and document `TanStack Table` as a planned but not yet selected option for a later advanced project table experience.

   Likely documents to update: `docs/STATUS.md`, `docs/USER-GUIDE.md`, `docs/context/interface-layer.md`, and frontend package metadata/lockfile.

   Expected validation: frontend lint, tests, and build; focused interaction tests for any introduced dialog, toast, dropdown, tab, tooltip, or icon-driven controls; and dependency review confirming the bundle remains aligned with the lightweight React/Vite direction.

   Planned semantic decision: patch bump from `0.3.27` to `0.3.28`, because this introduces frontend dependencies and user-facing UI primitives without changing backend contracts.

2. `docs(brand): define OrchFlow visual identity direction`

   Objective: define a low-risk visual identity reference before adding real logo assets to login, browser tab, desktop packaging, or other surfaces.

   Main scope: document the preferred logo concept as an original `OF` monogram where the `O` suggests a local flow/cycle and the `F` suggests an operational control path with small nodes; keep the work descriptive only; avoid Docker, Kubernetes, cloud, container, whale, ship, or other motifs that could create confusion or copyright/trademark risk.

   Likely documents to update: `docs/TO-DO.md`, `docs/context/interface-layer.md`, and a future brand/design note if the project adds one.

   Expected validation: documentation diff review only.

   Planned semantic decision: no version bump if the PR remains descriptive documentation only; patch bump if it introduces user-visible assets or interface changes.

3. `docs(installer): outline Windows installer and release matrix`

   Objective: capture installer and release-shape possibilities without committing the project to a desktop stack or packaging model before the web and launcher flows stabilize.

   Main scope: document the future discussion around a Windows-first bootstrap `.exe`, full-project `.zip` releases, and optional release models such as `CLI only`, `CLI + API`, `CLI + API + Web`, `CLI + API + Desktop App`, and `All included`; keep the first recommended direction as a lightweight bootstrap that reuses the explicit setup/control scripts; leave Tauri, Electron, and other desktop-shell choices undecided until a dedicated evaluation step.

   Likely documents to update: `docs/TO-DO.md`, `docs/USER-GUIDE.md`, `docs/context/devops-and-delivery.md`, and possibly `docs/PROJECT-ARCHITECTURE.md` only if the approved plan changes product scope.

   Expected validation: documentation diff review only.

   Planned semantic decision: no version bump if the PR remains planning documentation only; patch bump if it changes documented release workflow expectations.

## Cross-Cutting Rules

- expand the mirrored operator workflow in `CLI`, `API`, and `web` together whenever a new user-facing capability is intentionally introduced
- keep Windows `.bat` lifecycle scripts as the authoritative operational contract for managed projects in `v0.3.27`
- before starting any roadmap implementation step, verify the remote `main` state, update local `main` from the remote repository, and create the work branch from that synchronized baseline
- implement each roadmap step as a coherent Conventional Commit change unit and document the semantic version decision in the pull request
- keep each roadmap step small enough to be completed by one branch and one pull request; split larger themes into separate ordered steps before implementation
- evaluate version impact before starting a roadmap step and confirm it after the diff is complete, especially for AI assistance milestones such as the `AI Agent Adapter` and `LiteLLM` integration
- avoid container orchestration, remote orchestration, and speculative support layers unless a later approved requirement changes the product scope
- update `docs/STATUS.md`, `docs/USER-GUIDE.md`, and authorized scope-relevant context documentation whenever a roadmap milestone changes implemented behavior
- revisit future `mobile` and `desktop` planning only after the API and web flows are stable
