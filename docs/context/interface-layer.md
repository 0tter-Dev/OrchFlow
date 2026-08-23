# Interface Layer

## Purpose

This module defines the user-facing interface boundary for OrchFlow clients.

## Objective

Provide a clean separation between the backend core and multiple user-facing clients that consume the API.

## Current Status

`planned`

## Initial Clients

- `web`
- `mobile`
- `desktop`

## Focus Areas

- project listing
- project details
- runtime metrics display
- lifecycle controls
- admin user and permission visibility

## Key Rules

- interface clients should remain consumers of platform capabilities, not their owners
- interface clients should rely on the API-facing surface rather than bypassing application boundaries
- the `interface/` folder should act as a physical boundary between the backend core and client implementations
- visual complexity should remain secondary to operational clarity in `v0.1.0`
- the first concrete client direction is `web`, but the structure should allow future `mobile` and `desktop` clients

## Main Relationships

- depends on `External Surfaces`
- reflects `Access Control` capabilities
- displays data from `Runtime Inspection`
- triggers actions through `Lifecycle Orchestration`
