# External Surfaces

## Purpose

This module defines the non-visual delivery channels that expose OrchFlow capabilities.

## Objective

Expose the same core application behavior through both CLI and API without duplicating business rules.

## Current Status

`planned`

## Channels

- `CLI`
- `API`

## Key Rules

- CLI and API should mirror the same core use cases as closely as practical
- business logic must stay in the core application, not in the delivery layer
- authorization rules must be enforced consistently
- the API should be the primary backend entry point for interface clients

## Main Relationships

- depends on `Access Control`
- depends on `Project Registry`
- depends on `Lifecycle Orchestration`
- depends on `Runtime Inspection`
- may expose `AI Agent Adapter` workflows
