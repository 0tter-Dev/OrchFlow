# TO-DO

## Purpose

This document tracks the next planned steps for OrchFlow after the initial documentation foundation.

## Current Implementation Sequence

The completed implementation sequence now covers the backend bootstrap foundation, configuration plus persistence bootstrap, access-control foundation, project-registry foundation, lifecycle-orchestration foundation, runtime-inspection milestone, web-bootstrap milestone, the first practical web integration flow, and real project onboarding hardening for existing `.bat` scripts.

`v0.2.0` consolidates the first usable backend, `CLI`, `API`, and `web` baseline for authenticated operation of already registered projects, including project visibility, basic lifecycle execution, runtime inspection, and lifecycle controls backed by Windows `.bat` scripts.

The current frontend package manager decision is `pnpm`.

Implemented planning items should be removed from this document as work progresses so it remains focused on what comes next.

## Next Implementation Roadmap

The next implementation sequence should prioritize real local project operation with existing `.bat` lifecycle scripts before starting the optional `AI Agent Adapter` flow.

1. **Web Project Registration Flow**
   Add the first `interface/web` flow for registering an existing project with a `.bat` lifecycle script. The flow should collect project reference name, description, project root path, lifecycle script path, and optional lifecycle action mappings while continuing to use the existing API boundary.

2. **Lifecycle History And Audit Visibility**
   Expose recent operational history through the mirrored `API`, `CLI`, and `web` surfaces. The first useful view should cover project registration, project reads/listing, lifecycle actions, authentication events, and admin actions already recorded in audit storage.

3. **Admin And Ownership Management**
   Expand access-control and project-ownership workflows beyond bootstrap admin creation and user listing. This milestone should cover practical admin management for users, roles or activation state, and project ownership visibility or assignment while preserving explicit authorization rules.

4. **Runtime Inspection Refinement**
   Improve runtime diagnostics for real project operation. Priorities include basic reachability checks when `APP_URL` is available, clearer `unsupported` and `stopped` explanations, and a reviewed decision about whether lightweight runtime snapshots should be persisted.

5. **CI And Contract Hardening**
   Strengthen validation now that backend and frontend flows are real. This milestone should add migration validation, API contract coverage, critical web-flow tests, and CI execution for backend checks plus frontend lint, tests, and build.

6. **AI Agent Adapter Foundation**
   Start the optional AI-assisted onboarding foundation only after the non-AI project workflow is stable. The first AI milestone should define the provider-agnostic boundary, local provider configuration, detection of available `Ollama` or compatible local models, and authorized project analysis without automatic file writes.

## Cross-Cutting Rules

- expand the mirrored operator workflow in `CLI`, `API`, and `web` together whenever a new user-facing capability is intentionally introduced
- keep Windows `.bat` lifecycle scripts as the authoritative operational contract for managed projects in `v0.2.0`
- avoid container orchestration, remote orchestration, and speculative support layers unless a later approved requirement changes the product scope
- update `docs/STATUS.md`, `docs/USER-GUIDE.md`, and authorized scope-relevant context documentation whenever a roadmap milestone changes implemented behavior
- revisit future `mobile` and `desktop` planning only after the API and web flows are stable
