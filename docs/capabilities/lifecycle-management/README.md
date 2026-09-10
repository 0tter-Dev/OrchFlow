# Lifecycle Orchestration

## Purpose

This module defines how OrchFlow controls a project's operational lifecycle.

## Objective

Provide a standardized lifecycle engine for local projects using an explicit `.bat` operational contract.

## Current Status

`implemented`

## Core Actions

- `status`
- `start`
- `stop`
- `restart`

## Key Rules

- lifecycle actions must not rely on UI-specific logic
- actions must run against normalized project definitions
- lifecycle execution must go through a project-agnostic adapter boundary
- OrchFlow should resolve project-specific action mappings before attempting lifecycle execution
- lifecycle execution should be available only for functions that are configured for the project
- undefined or explicitly unconfigured lifecycle functions should produce clear operator-facing feedback instead of attempting script execution
- lifecycle transitions should be auditable
- the system should validate whether lifecycle actions succeeded through runtime inspection when possible
- the first practical execution flow may rely on command-dispatch by script argument while the project remains Windows-first

## Implemented Baseline

- lifecycle actions execute through the Windows batch adapter using canonical actions resolved per project
- successful and failed executions are audited with command identifiers, exit status, success state, and runtime status when inspection is available
- runtime inspection is invoked after lifecycle execution when available so API and CLI receive an immediate runtime summary

## Lifecycle Configuration Enforcement

The orchestration layer now consumes project lifecycle mappings from the registry before adapter execution. Projects with partial configuration execute only configured lifecycle actions. Undefined actions, explicitly unconfigured actions, and projects with no configured lifecycle function are blocked from operational lifecycle execution until the user maps at least one function.

## Main Relationships

- depends on `Project Registry`
- depends on `Project Adapter`
- uses `Runtime Inspection`
- is constrained by `Access Control`
- emits records to `Persistence And Audit`
