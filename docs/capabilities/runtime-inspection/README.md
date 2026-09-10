# Runtime Inspection

## Purpose

This module defines how OrchFlow observes project runtime state after or during lifecycle actions.

## Objective

Expose practical operational facts for local project control and troubleshooting.

## Current Status

`implemented`

## Target Runtime Data

- ports
- process identifiers
- uptime
- CPU usage
- memory usage
- basic health or reachability indicators when applicable

## Key Rules

- runtime inspection should support lifecycle validation
- collected data should remain understandable to a human operator
- the first version should focus on useful local operational facts rather than deep telemetry
- the first implemented version should prioritize Windows-local inspection derived from the managed `.bat` contract
- API and CLI should expose the same inspection capability whenever it is available to operators
- batch inspection should reuse the same per-project authorization rules as direct inspection and should not create a separate visibility shortcut

## Implemented Baseline

- extracts runtime hints such as `APP_PORT` and `APP_URL` from the registered lifecycle script
- inspects Windows listening ports and associates them with process identifiers when possible
- captures lightweight process snapshots including PID, process name, CPU, memory, and start time
- derives a practical `running`, `stopped`, or `unsupported` runtime state for operator consumption, including `APP_URL`-only running detection when no `APP_PORT` is available
- includes an operator-facing status explanation so `stopped`, timeout, missing-hint, and `unsupported` states are clearer
- feeds web operational readiness so selected projects can surface runtime diagnostics beside direct refresh actions
- checks basic `APP_URL` reachability when an application URL is available and reports timeout or connection failure details in the status explanation
- exposes the inspection timestamp with the runtime snapshot
- is available as a direct inspection use case, a requested multi-project batch inspection use case, and as a post-lifecycle validation step
- batch inspection accepts explicit project identifiers, deduplicates repeated IDs, preserves the requested project order, and inspects only projects visible to the authenticated operator
- does not persist runtime snapshots yet; snapshot persistence was evaluated during runtime maturity work and remains deferred until there is a concrete review or history need beyond audit events and on-demand inspection

## Main Relationships

- supports `Lifecycle Orchestration`
- feeds `External Surfaces`
- feeds `Interface Layer`
- may support AI-assisted project analysis with safe, explicit boundaries
- may store snapshots or events through `Persistence And Audit`
