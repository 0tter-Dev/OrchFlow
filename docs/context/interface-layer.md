# Interface Layer

## Purpose

This module defines the visual user-facing interface for OrchFlow.

## Objective

Provide a simple and efficient way to inspect project status, review metrics, and trigger lifecycle actions.

## Current Status

`planned`

## Focus Areas

- project listing
- project details
- runtime metrics display
- lifecycle controls
- admin user and permission visibility

## Key Rules

- the interface should remain a consumer of platform capabilities, not their owner
- the interface should rely on the API-facing surface rather than bypassing application boundaries
- visual complexity should remain secondary to operational clarity in `v0.1.0`

## Main Relationships

- depends on `External Surfaces`
- reflects `Access Control` capabilities
- displays data from `Runtime Inspection`
- triggers actions through `Lifecycle Orchestration`
