# TO-DO

## Purpose

This document tracks the next planned steps for OrchFlow after the initial documentation foundation.

## Current Implementation Sequence

The completed implementation sequence now covers the backend bootstrap foundation, configuration plus persistence bootstrap, access-control foundation, project-registry foundation, lifecycle-orchestration foundation, runtime-inspection milestone, web-bootstrap milestone, the first practical web integration flow, real project onboarding hardening for existing `.bat` scripts, the first web project registration flow, lifecycle history plus audit visibility, admin plus project ownership management, runtime inspection refinement, CI plus contract hardening, documentation/versioning governance for pull requests, the LiteLLM dependency plus disabled-by-default AI configuration baseline, the first domain-level ideal lifecycle function model, automatic lifecycle script detection with derived configuration health, API/CLI workflows for manual lifecycle mapping plus explicit `unconfigured` decisions, explicit project reload for one project or multiple projects in sequence, lifecycle execution gating for partial or blocked configurations, web lifecycle configuration indicators plus mapping controls, the authenticated AI assistance boundary with a LiteLLM gateway status client, LiteLLM gateway health plus model discovery through API and CLI, authorized project context manifests, reviewable AI analysis proposals without file writes, API/CLI proposal review decisions with validation, pytest cache relocation to `runtime/pytest-cache`, explicit approved proposal application that writes lifecycle `.bat` files and persists effective `ai_approved` mappings only after separate user confirmations, non-AI API/CLI project update workflows for metadata, lifecycle script paths, and lifecycle mappings, runtime inspection maturity for `APP_URL`-only projects, unsupported no-hint diagnostics, URL timeout explanations, filtered admin audit history across API, CLI, and web, web project editing for metadata plus lifecycle paths, web AI proposal review/application, web guided operational readiness for lifecycle and runtime diagnostics, richer web API/validation error states, roadmap governance that treats each planned step as one pull-request-sized change, web guided onboarding polish for first-project and selected-project states, focused AI API contract tests, version consistency contract tests, hardened Alembic revision graph plus schema drift tests, manual release tag validation plus release-note artifact generation, and the Windows-first local development launcher.

`v0.3.19` consolidates the first usable backend, `CLI`, `API`, and `web` baseline for authenticated operation of registered projects, including project visibility, project metadata/script update workflows, web project editing, lifecycle execution, refined runtime inspection for `APP_URL`-only projects and clearer timeout/unsupported diagnostics, guided operational readiness, first-project and selected-project onboarding guidance, richer API and validation error notices, roadmap planning at one-PR granularity, focused AI API contract tests, version consistency contract tests, hardened Alembic revision graph plus schema drift tests, manual release tag validation plus release-note artifact generation, a Windows-first local development launcher, filtered admin audit visibility, user and ownership management, CI validation, lifecycle controls backed by Windows `.bat` scripts, preferred-action detection, project configuration health, reviewable manual lifecycle configuration decisions, explicit reload after local `.bat` changes, configured-action execution enforcement, web mapping controls, authenticated AI assistance status, LiteLLM gateway health, LiteLLM model discovery, authorized context manifests, reviewable AI analysis proposals, proposal review decisions, confirmed application of approved proposals, and web AI proposal review/application.

The current frontend package manager decision is `pnpm`.

Implemented planning items should be removed from this document as work progresses so it remains focused on what comes next. Roadmap items should be granular by default: each numbered step should describe one coherent pull-request-sized change, not a broad workstream that requires multiple pull requests to finish. When a planned workstream is still too broad, split it into sequential steps before implementation starts.

## Next Implementation Roadmap

The next implementation sequence should improve OrchFlow's own local initialization flow first, then reshape the web operator surface around daily project control, runtime visibility, and later dashboard growth. Each numbered step below is intended to fit one short-lived branch, one Conventional Commit, and one pull request.

1. `feat(devx): add Windows launcher bootstrap`

   Objective: provide a Windows-first `orchflow-dev.bat` entrypoint that helps a newly cloned repository move from missing local setup to running `CLI`, `API`, and `web` surfaces with clear operator-facing checks.

   Main scope: verify required local tools such as `uv`, Node/Corepack, and `pnpm`; create local `.env` files from committed examples without overwriting existing local files; install backend and web dependencies; run Alembic setup; validate basic CLI/API readiness; and start API plus Vite web development servers through explicit user-controlled steps.

   Likely documentation updates: `docs/TO-DO.md`, `docs/STATUS.md`, `docs/USER-GUIDE.md`, `README.md`, and `docs/context/configuration-and-environment.md`.

   Expected validation: launcher smoke test or static command-shape check where practical, `uv run ruff check .`, `uv run mypy src`, `uv run pytest`, and the relevant frontend install/build checks if the launcher touches web setup behavior.

   Expected version decision: patch bump to `0.3.19`, because this adds a user-facing local setup workflow without changing OrchFlow's core product scope.

2. `feat(preferences): add user web preferences`

   Objective: persist lightweight per-user interface preferences so the web client can support future customization without relying only on browser-local state.

   Main scope: add backend-owned user preference storage for locale, project view mode, and global status refresh interval; expose authenticated API and mirrored CLI access if intentionally surfaced; consume the preference contract from the web client; and keep defaults development-friendly.

   Likely documentation updates: `docs/TO-DO.md`, `docs/STATUS.md`, `docs/USER-GUIDE.md`, `docs/INDEX.md` if relationships change, and `docs/context/access-control.md`, `docs/context/interface-layer.md`, and `docs/context/persistence-and-audit.md`.

   Expected validation: Alembic migration validation, backend contract and integration tests for preference authorization and defaults, frontend tests for preference loading and updates, `uv run ruff check .`, `uv run mypy src`, `uv run pytest`, `pnpm lint`, `pnpm test`, and `pnpm build`.

   Expected version decision: patch bump to `0.3.20`, because this adds a narrow authenticated preference capability and persistence contract inside the current `0.3.x` line.

3. `feat(runtime): add batch runtime inspection`

   Objective: let the web operator surface refresh status for visible projects without issuing only one selected-project runtime request at a time.

   Main scope: add an application-level use case for inspecting multiple authorized projects, expose it through API and CLI, preserve role plus ownership checks, return compact per-project runtime summaries, and keep runtime snapshot persistence deferred unless a concrete history need is introduced.

   Likely documentation updates: `docs/TO-DO.md`, `docs/STATUS.md`, `docs/USER-GUIDE.md`, `docs/INDEX.md` if relationships change, and `docs/context/runtime-inspection.md`, `docs/context/external-surfaces.md`, and `docs/context/interface-layer.md`.

   Expected validation: backend authorization tests, API and CLI contract coverage for multi-project inspection, runtime inspection tests for partial failures or unsupported projects, `uv run ruff check .`, `uv run mypy src`, and `uv run pytest`.

   Expected version decision: patch bump to `0.3.21`, because this expands an existing runtime capability through mirrored external surfaces without changing the local-first architecture.

4. `feat(web): redesign operator workspace`

   Objective: replace the current bootstrap-style web presentation with a practical daily operator workspace inspired by tools such as Docker Desktop while staying specific to OrchFlow's local `.bat` lifecycle model.

   Main scope: remove hero-oriented presentation from the authenticated workspace; add a compact application shell with project navigation, toolbar, project list/table mode, lifecycle action buttons, runtime status summaries, readiness warnings, settings entrypoints, and simple `pt-BR` plus `en-US` text dictionaries; add `lucide-react` for recognizable action icons; and use backend preferences plus batch runtime inspection when available.

   Likely documentation updates: `docs/TO-DO.md`, `docs/STATUS.md`, `docs/USER-GUIDE.md`, `README.md`, and `docs/context/interface-layer.md`.

   Expected validation: critical web-flow tests for project selection, lifecycle action availability, readiness indicators, view-mode switching, locale switching, refresh interval behavior, and responsive layout basics; `pnpm lint`, `pnpm test`, and `pnpm build`; backend validation only if this PR touches shared contracts.

   Expected version decision: patch bump to `0.3.22`, because this is a meaningful web UX improvement built on existing product capabilities inside the current milestone line.

5. `feat(registry): add project unlink workflow`

   Objective: let users remove a project from their OrchFlow workspace without deleting the local project folder or lifecycle `.bat` file.

   Main scope: add a registry-owned unlink operation with authorization, audit events, API and CLI exposure, web action affordance, clear copy that the local files are preserved, and admin/member behavior aligned with the current ownership model.

   Likely documentation updates: `docs/TO-DO.md`, `docs/STATUS.md`, `docs/USER-GUIDE.md`, `docs/INDEX.md` if relationships change, and `docs/context/project-registry.md`, `docs/context/external-surfaces.md`, `docs/context/interface-layer.md`, and `docs/context/persistence-and-audit.md`.

   Expected validation: backend registry tests, authorization tests, API and CLI contract tests, web tests for unlink confirmation and list refresh, `uv run ruff check .`, `uv run mypy src`, `uv run pytest`, `pnpm lint`, `pnpm test`, and `pnpm build`.

   Expected version decision: patch bump to `0.3.23`, because this adds a focused project registry capability with visible API, CLI, and web behavior.

## Cross-Cutting Rules

- expand the mirrored operator workflow in `CLI`, `API`, and `web` together whenever a new user-facing capability is intentionally introduced
- keep Windows `.bat` lifecycle scripts as the authoritative operational contract for managed projects in `v0.3.19`
- implement each roadmap step as a coherent Conventional Commit change unit and document the semantic version decision in the pull request
- keep each roadmap step small enough to be completed by one branch and one pull request; split larger themes into separate ordered steps before implementation
- evaluate version impact before starting a roadmap step and confirm it after the diff is complete, especially for AI assistance milestones such as the `AI Agent Adapter` and `LiteLLM` integration
- avoid container orchestration, remote orchestration, and speculative support layers unless a later approved requirement changes the product scope
- update `docs/STATUS.md`, `docs/USER-GUIDE.md`, and authorized scope-relevant context documentation whenever a roadmap milestone changes implemented behavior
- revisit future `mobile` and `desktop` planning only after the API and web flows are stable
