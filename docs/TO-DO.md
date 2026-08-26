# TO-DO

## Purpose

This document tracks the next planned steps for OrchFlow after the initial documentation foundation.

## Current Implementation Sequence

The completed implementation sequence now covers the backend bootstrap foundation, configuration plus persistence bootstrap, access-control foundation, project-registry foundation, lifecycle-orchestration foundation, runtime-inspection milestone, web-bootstrap milestone, the first practical web integration flow, real project onboarding hardening for existing `.bat` scripts, the first web project registration flow, lifecycle history plus audit visibility, admin plus project ownership management, runtime inspection refinement, and CI plus contract hardening.

`v0.2.0` consolidates the first usable backend, `CLI`, `API`, and `web` baseline for authenticated operation of already registered projects, including project visibility, basic lifecycle execution, runtime inspection, and lifecycle controls backed by Windows `.bat` scripts.

The current frontend package manager decision is `pnpm`.

Implemented planning items should be removed from this document as work progresses so it remains focused on what comes next.

## Next Implementation Roadmap

The next implementation sequence should prioritize real local project operation with existing `.bat` lifecycle scripts before starting the optional `AI Agent Adapter` flow.

1. **AI Agent Adapter Foundation**
   Start the optional AI-assisted onboarding foundation only after the non-AI project workflow is stable. The first AI milestone should define the provider-agnostic boundary, local provider configuration, detection of available `Ollama` or compatible local models, and authorized project analysis without automatic file writes.

## Cross-Cutting Rules

- expand the mirrored operator workflow in `CLI`, `API`, and `web` together whenever a new user-facing capability is intentionally introduced
- keep Windows `.bat` lifecycle scripts as the authoritative operational contract for managed projects in `v0.2.0`
- avoid container orchestration, remote orchestration, and speculative support layers unless a later approved requirement changes the product scope
- update `docs/STATUS.md`, `docs/USER-GUIDE.md`, and authorized scope-relevant context documentation whenever a roadmap milestone changes implemented behavior
- revisit future `mobile` and `desktop` planning only after the API and web flows are stable
