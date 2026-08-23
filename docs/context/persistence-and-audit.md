# Persistence And Audit

## Purpose

This module defines how OrchFlow stores its local operational data and retains action history.

## Objective

Provide lightweight but reliable persistence for a local-first orchestration workflow.

## Current Status

`planned`

## Initial Direction

The preferred initial persistence direction is `SQLite`.

## Target Stored Data

- users
- permissions
- projects
- project ownership metadata
- lifecycle definitions
- project-specific lifecycle action mappings
- runtime-related snapshots when appropriate
- lifecycle and audit events

## Key Rules

- persistence concerns must remain outside the core domain logic
- lifecycle actions should leave an audit trail
- AI-assisted inspection and script generation authorizations should be auditable
- lifecycle action mapping changes should be auditable with user attribution
- the system should prioritize practical local reliability over premature complexity

## Main Relationships

- supports `Access Control`
- supports `Project Registry`
- supports `Lifecycle Orchestration`
- may retain outputs from `Runtime Inspection`
