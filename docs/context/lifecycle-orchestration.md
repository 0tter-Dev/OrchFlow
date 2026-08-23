# Lifecycle Orchestration

## Purpose

This module defines how OrchFlow controls a project's operational lifecycle.

## Objective

Provide a standardized lifecycle engine for local projects using an explicit `.bat` operational contract.

## Current Status

`planned`

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
- lifecycle transitions should be auditable
- the system should validate whether lifecycle actions succeeded through runtime inspection when possible

## Main Relationships

- depends on `Project Registry`
- depends on `Project Adapter`
- uses `Runtime Inspection`
- is constrained by `Access Control`
- emits records to `Persistence And Audit`
