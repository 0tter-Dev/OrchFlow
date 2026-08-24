# TO-DO

## Purpose

This document tracks the next planned steps for OrchFlow after the initial documentation foundation.

## Current Implementation Sequence

The near-term implementation plan is organized into the next pull request after the completed backend bootstrap foundation, configuration plus persistence bootstrap, access-control foundation, project-registry foundation, lifecycle-orchestration foundation, runtime-inspection milestone, and web-bootstrap milestone.

The current frontend package manager decision is `pnpm`.

Implemented planning items should be removed from this document as work progresses so it remains focused on what comes next.

## PR 8: First Web Integration With Auth And Projects

### Purpose

Connect the web client to the stabilized backend contracts for the first useful operator flow.

### Planned Scope

- implement login flow against the API
- implement project listing and project detail views
- display basic runtime status information
- wire the first lifecycle control actions through the API
- validate the initial end-to-end contract between backend and web

### Local Validation

- `uv sync --dev`
- `uv run ruff check .`
- `uv run mypy src`
- `uv run pytest`
- `corepack enable`
- `pnpm install`
- `pnpm lint`
- `pnpm test`
- `pnpm build`

### Manual Git And GitHub Steps

- create branch `feat/web-project-integration`
- validate both backend and frontend locally before opening the PR
- open a PR with explicit notes about API contracts consumed by the web client

## Cross-Cutting Follow-Ups To Keep Visible

- tighten CI as tests and build scripts become real instead of bootstrap placeholders
- add backend contract and migration validation once API and persistence stabilize
- revisit future `mobile` and `desktop` planning only after the API and web flows are stable
- avoid speculative support layers for containers or shared kernels unless a later approved requirement makes them necessary
- evaluate broader lifecycle script compatibility beyond the current Windows command-dispatch-by-argument assumption in a future approved step if real project scripts require it
