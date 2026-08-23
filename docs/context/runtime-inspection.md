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

## Implemented Baseline

- extracts runtime hints such as `APP_PORT` and `APP_URL` from the registered lifecycle script
- inspects Windows listening ports and associates them with process identifiers when possible
- captures lightweight process snapshots including PID, process name, CPU, memory, and start time
- derives a practical `running`, `stopped`, or `unsupported` runtime state for operator consumption
- is available as a direct inspection use case and as a post-lifecycle validation step

## Main Relationships

- supports `Lifecycle Orchestration`
- feeds `External Surfaces`
- feeds `Interface Layer`
- may support AI-assisted project analysis with safe, explicit boundaries
- may store snapshots or events through `Persistence And Audit`
