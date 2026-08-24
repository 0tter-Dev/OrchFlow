# Interface Layer

## Purpose

This module defines the user-facing interface boundary for OrchFlow clients.

## Objective

Provide a clean separation between the backend core and multiple user-facing clients that consume the API.

## Current Status

`in_progress`

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
- visual complexity should remain secondary to operational clarity in `v0.1.2`
- the first concrete client direction is `web`, but the structure should allow future `mobile` and `desktop` clients

## Implemented Baseline

- `interface/web` now exists as the first concrete interface client
- the web client is bootstrapped with `React`, `TypeScript`, `Vite`, and `pnpm`
- the initial web surface validates API consumption through a shared client boundary and a backend health-check screen
- frontend lint, test, and build scripts are established so later feature work can focus on real operator flows

## Main Relationships

- depends on `External Surfaces`
- reflects `Access Control` capabilities
- displays data from `Runtime Inspection`
- triggers actions through `Lifecycle Orchestration`
