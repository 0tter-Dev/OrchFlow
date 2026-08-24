# TO-DO

## Purpose

This document tracks the next planned steps for OrchFlow after the initial documentation foundation.

## Current Implementation Sequence

The completed implementation sequence now covers the backend bootstrap foundation, configuration plus persistence bootstrap, access-control foundation, project-registry foundation, lifecycle-orchestration foundation, runtime-inspection milestone, web-bootstrap milestone, and the first practical web integration flow.

The current frontend package manager decision is `pnpm`.

Implemented planning items should be removed from this document as work progresses so it remains focused on what comes next.

## Next Planning Decision

The next pull request after `PR 8` should be defined only after review of the new web baseline, so the roadmap stays aligned with the most valuable next operator workflow instead of locking a premature sequence.

## Cross-Cutting Follow-Ups To Keep Visible

- define the next post-`PR 8` milestone only after reviewing the practical behavior of the current web surface against real local projects
- tighten CI as tests and build scripts become real instead of bootstrap placeholders
- add backend contract and migration validation once API and persistence stabilize
- expand the mirrored operator workflow in `CLI`, `API`, and `web` together whenever a new user-facing capability is intentionally introduced
- revisit future `mobile` and `desktop` planning only after the API and web flows are stable
- avoid speculative support layers for containers or shared kernels unless a later approved requirement makes them necessary
- evaluate broader lifecycle script compatibility beyond the current Windows command-dispatch-by-argument assumption in a future approved step if real project scripts require it
