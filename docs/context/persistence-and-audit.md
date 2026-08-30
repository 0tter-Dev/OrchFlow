# Persistence And Audit

## Purpose

This module defines how OrchFlow stores its local operational data and retains action history.

## Objective

Provide lightweight but reliable persistence for a local-first orchestration workflow.

## Current Status

`implemented`

## Initial Direction

The preferred initial persistence direction is `SQLite`.

## Target Stored Data

- users
- permissions
- projects
- project ownership metadata
- lifecycle definitions
- project-specific lifecycle action mappings
- lifecycle function configuration states
- runtime-related snapshots when appropriate
- AI analysis sessions and allowed-context manifests
- AI-generated proposals, review decisions, and approved file or mapping changes
- lifecycle and audit events

## Implemented Baseline

- audit events are persisted in local `SQLite` storage
- access-control operations record user registration, login, and admin user listing events
- project registry operations record project registration, list, and read events
- planned registry refinements should record reload operations and automatic mapping refreshes
- current registration persists automatically detected preferred mappings as imported lifecycle action mappings
- manual mapping decisions and explicit unconfigured-function decisions are persisted with actor metadata and audited through project lifecycle configuration update events
- lifecycle operations record action, command identifier, exit status, success state, and runtime status when available
- recent audit history is exposed to authenticated admins through `CLI`, `API`, and the web operator workspace
- admin user updates and project ownership changes are audited

## Key Rules

- persistence concerns must remain outside the core domain logic
- lifecycle actions should leave an audit trail
- recent audit history visibility must stay permissioned to admins until finer-grained operational history rules are intentionally designed
- AI-assisted inspection and script generation authorizations should be auditable
- LiteLLM-backed model invocation metadata should be auditable without storing secrets or unnecessary prompt contents
- authorized context manifests should persist selected project, selected model, intended operation, include/exclude path metadata, ignored/generated artifact metadata, secret filtering rules, size limits, and total authorized byte counts without storing file contents or secret values
- AI analysis proposals should persist structured proposal output, selected model, manifest relationship, requesting user, lifecycle strategy, runtime hints, candidate script content, warnings, and proposed mappings without storing secrets or unnecessary prompt contents
- AI proposal approval and rejection decisions should be auditable
- lifecycle action mapping changes should be auditable with user attribution
- project reload and lifecycle configuration health changes should be auditable when they affect controllability or operator guidance
- the system should prioritize practical local reliability over premature complexity
- the initial persistence bootstrap should provide a real migration path early, even before the first business entities are fully implemented

## Main Relationships

- supports `Access Control`
- supports `Project Registry`
- supports `Lifecycle Orchestration`
- may retain outputs from `Runtime Inspection`
