# TO-DO

## Purpose

This document tracks the next planned steps for OrchFlow after the initial documentation foundation.

## Current Implementation Sequence

The completed implementation sequence now covers the backend bootstrap foundation, configuration plus persistence bootstrap, access-control foundation, project-registry foundation, lifecycle-orchestration foundation, runtime-inspection milestone, web-bootstrap milestone, the first practical web integration flow, real project onboarding hardening for existing `.bat` scripts, the first web project registration flow, lifecycle history plus audit visibility, admin plus project ownership management, runtime inspection refinement, CI plus contract hardening, documentation/versioning governance for pull requests, the LiteLLM dependency plus disabled-by-default AI configuration baseline, the first domain-level ideal lifecycle function model, automatic lifecycle script detection with derived configuration health, API/CLI workflows for manual lifecycle mapping plus explicit `unconfigured` decisions, explicit project reload for one project or multiple projects in sequence, lifecycle execution gating for partial or blocked configurations, web lifecycle configuration indicators plus mapping controls, the authenticated AI assistance boundary with a LiteLLM gateway status client, LiteLLM gateway health plus model discovery through API and CLI, authorized project context manifests, reviewable AI analysis proposals without file writes, API/CLI proposal review decisions with validation, pytest cache relocation to `runtime/pytest-cache`, explicit approved proposal application that writes lifecycle `.bat` files and persists effective `ai_approved` mappings only after separate user confirmations, non-AI API/CLI project update workflows for metadata, lifecycle script paths, and lifecycle mappings, runtime inspection maturity for `APP_URL`-only projects, unsupported no-hint diagnostics, URL timeout explanations, filtered admin audit history across API, CLI, and web, web project editing for metadata plus lifecycle paths, web AI proposal review/application, web guided operational readiness for lifecycle and runtime diagnostics, richer web API/validation error states, roadmap governance that treats each planned step as one pull-request-sized change, web guided onboarding polish for first-project and selected-project states, focused AI API contract tests, version consistency contract tests, hardened Alembic revision graph plus schema drift tests, manual release tag validation plus release-note artifact generation, split Windows setup and control launchers, PID-based local API and web process control, backend-owned user web preferences for locale, project display mode, and status refresh interval across API, CLI, and web, authorized batch runtime inspection for visible projects across API, CLI, and web, the compact web operator workspace redesign, the project unlink workflow across API, CLI, and web, the focused unauthenticated web login plus account-creation flow, stabilized authenticated web health refresh that keeps the latest known API snapshot visible during refresh attempts and transient failures, the first accessible web UI primitives plus operational icon baseline using Radix Tabs, Radix Tooltip, and `lucide-react`, the descriptive OrchFlow visual identity direction for a future original `OF` monogram, the descriptive Windows installer plus release-shape planning reference, and completed web authentication UX with automatic login after account creation, visible session feedback, and password visibility control.

`v0.3.29` consolidates the first usable backend, `CLI`, `API`, and `web` baseline for authenticated operation of registered projects, including project visibility, project metadata/script update workflows, project unlink without local file deletion, web project editing, lifecycle execution, refined runtime inspection for `APP_URL`-only projects and clearer timeout/unsupported diagnostics, authorized multi-project runtime inspection, a compact daily operator workspace, stable authenticated health refresh that preserves the latest known API snapshot through refresh loading and transient failures, a focused unauthenticated web authentication surface with `Login` and role-neutral `Create account`, automatic login after account creation, direct login transition into the workspace, visible auth progress/error feedback, password visibility control, Radix-backed authentication tabs, a shared Radix tooltip wrapper, `lucide-react` operational icons, simple `pt-BR` and `en-US` shell text dictionaries, guided operational readiness, first-project and selected-project onboarding guidance, richer API and validation error notices, roadmap planning at one-PR granularity, focused AI API contract tests, version consistency contract tests, hardened Alembic revision graph plus schema drift tests, manual release tag validation plus release-note artifact generation, split Windows setup and control launchers, PID-based local API and web process control, backend-owned user web preferences, filtered admin audit visibility, user and ownership management, CI validation, lifecycle controls backed by Windows `.bat` scripts, preferred-action detection, project configuration health, reviewable manual lifecycle configuration decisions, explicit reload after local `.bat` changes, configured-action execution enforcement, web mapping controls, authenticated AI assistance status, LiteLLM gateway health, LiteLLM model discovery, authorized context manifests, reviewable AI analysis proposals, proposal review decisions, confirmed application of approved proposals, and web AI proposal review/application.

The current frontend package manager decision is `pnpm`.

Implemented planning items should be removed from this document as work progresses so it remains focused on what comes next. Roadmap items should be granular by default: each numbered step should describe one coherent pull-request-sized change, not a broad workstream that requires multiple pull requests to finish. When a planned workstream is still too broad, split it into sequential steps before implementation starts.

## Next Implementation Roadmap

1. `feat(devx): add unified OrchFlow launcher`

   Objective: simplify local startup by making `orchflow.bat` the single root-level user entrypoint while preserving the setup and control launchers as explicit implementation paths.

   Main scope: add root-level `orchflow.bat` with a compact menu for `[1] Run checks and start OrchFlow`, `[2] Open in browser`, `[3] Go to Setup menu`, `[4] Go to Control menu`, and `[0] Exit`; move auxiliary Windows launchers into `tools/windows/`; update script references so setup and control behavior remain separated internally; preserve existing local `.env`, runtime PID, process metadata, and explicit prerequisite behavior; and keep the flow Windows-first without introducing installer or desktop-shell dependencies.

   Likely documents to update: `README.md`, `docs/STATUS.md`, `docs/USER-GUIDE.md`, `docs/INSTALLER-AND-RELEASES.md`, `docs/context/devops-and-delivery.md`, and any script references in root documentation.

   Expected validation: run the relevant launcher paths on Windows where practical, plus backend and frontend validation commands affected by setup/control script changes; inspect script behavior for missing tool handling, process tracking, and browser-opening behavior.

   Planned semantic decision: patch bump from `0.3.29` to `0.3.30`, because this changes the documented local startup workflow while preserving the existing operational model.

2. `docs(installer): define Windows bootstrap executable implementation plan`

   Objective: turn the existing installer/release planning note into an implementation-ready plan for a future lightweight Windows bootstrap `.exe` without building the executable yet.

   Main scope: define what the bootstrap executable should validate, what it may delegate to `orchflow.bat` and `tools/windows/` scripts, how it should report prerequisite/setup failures, how it should open the local web UI after startup, what it must not install or control automatically, and what validation/release artifacts a later prototype PR would need.

   Likely documents to update: `docs/INSTALLER-AND-RELEASES.md`, `docs/TO-DO.md`, `docs/context/devops-and-delivery.md`, and possibly `docs/USER-GUIDE.md`.

   Expected validation: documentation diff review only.

   Planned semantic decision: no version bump if the PR remains implementation planning only; patch bump if it changes current setup or release workflow expectations.

3. `feat(installer): add Windows bootstrap executable prototype`

   Objective: provide the first experimental Windows bootstrap executable that helps users validate setup, start OrchFlow locally, and open the web UI through the documented launcher flow.

   Main scope: choose a minimal implementation path from the approved installer plan; build a lightweight bootstrap that delegates to `orchflow.bat` and the existing setup/control scripts; avoid hidden global dependency installation; preserve local-first files and explicit user-owned project boundaries; document how to build and validate the prototype; and keep desktop shell choices such as Tauri or Electron out of scope.

   Likely documents to update: `README.md`, `docs/STATUS.md`, `docs/USER-GUIDE.md`, `docs/INSTALLER-AND-RELEASES.md`, `docs/context/devops-and-delivery.md`, and release/build documentation added by the prototype.

   Expected validation: executable build validation, Windows smoke test for prerequisite checks and local startup, browser-open behavior validation, backend validation, frontend validation, and release artifact review if an artifact is generated.

   Planned semantic decision: patch bump from the then-current version, because this introduces a new user-facing startup artifact while staying inside the current Windows-first local workflow.

Currently deferred: web-based control of the OrchFlow process lifecycle itself. That idea may be revisited later, but it is intentionally excluded from the current Roadmap because stopping or restarting the API from the API-consuming web interface can create unclear failure modes.

## Cross-Cutting Rules

- expand the mirrored operator workflow in `CLI`, `API`, and `web` together whenever a new user-facing capability is intentionally introduced
- keep Windows `.bat` lifecycle scripts as the authoritative operational contract for managed projects in `v0.3.29`
- before starting any roadmap implementation step, verify the remote `main` state, update local `main` from the remote repository, and create the work branch from that synchronized baseline
- implement each roadmap step as a coherent Conventional Commit change unit and document the semantic version decision in the pull request
- keep each roadmap step small enough to be completed by one branch and one pull request; split larger themes into separate ordered steps before implementation
- evaluate version impact before starting a roadmap step and confirm it after the diff is complete, especially for AI assistance milestones such as the `AI Agent Adapter` and `LiteLLM` integration
- avoid container orchestration, remote orchestration, and speculative support layers unless a later approved requirement changes the product scope
- update `docs/STATUS.md`, `docs/USER-GUIDE.md`, and authorized scope-relevant context documentation whenever a roadmap milestone changes implemented behavior
- revisit future `mobile` and `desktop` planning only after the API and web flows are stable
