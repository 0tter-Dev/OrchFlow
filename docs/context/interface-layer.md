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
- lifecycle function configuration indicators
- guided operational readiness indicators
- AI proposal review and application controls
- audit history visibility
- admin user and ownership management

## Key Rules

- interface clients should remain consumers of platform capabilities, not their owners
- interface clients should rely on the API-facing surface rather than bypassing application boundaries
- the `interface/` folder should act as a physical boundary between the backend core and client implementations
- visual complexity should remain secondary to operational clarity in `v0.3.11`
- interface clients should communicate lifecycle configuration health without blocking partially configured projects
- the first concrete client direction is `web`, but the structure should allow future `mobile` and `desktop` clients

## Planned Configuration Experience

Interface clients should display lifecycle configuration health derived from the ideal lifecycle model:

- `complete`: all ideal lifecycle functions are configured
- `partial`: at least one function is configured, but one or more functions are undefined or unconfigured
- `blocked`: no function is configured

Partial projects should remain usable and should display a warning with access to function mapping details, manual configuration, and AI-assisted `.bat` improvement. The web workspace may use the AI proposal review/application panel for that improvement path when AI assistance is configured. Blocked projects should display an error state explaining that at least one lifecycle function must be configured before OrchFlow can operate the project.

The exact visual component is not fixed. A warning indicator, details popover, modal, or dedicated configuration panel are acceptable as long as the interface remains clear and operator-focused.

## Implemented Baseline

- `interface/web` now exists as the first concrete interface client
- the web client is bootstrapped with `React`, `TypeScript`, `Vite`, and `pnpm`
- the web client now consumes authenticated API flows through a shared client boundary
- the current web baseline includes session loading, login, project registration for existing `.bat` scripts, project listing, project details, project metadata and path editing, refined runtime visibility with reachability and status explanations, operational readiness guidance, lifecycle controls, AI proposal review/application, filtered recent audit history visibility for admins, user role/activation management, and project owner management
- project editing is now available through backend API and CLI contracts and through the web project detail view
- AI proposal review/application is now available through the web operator workspace using the existing authenticated AI assistance API contracts
- operational readiness now gives selected projects a compact lifecycle/runtime checklist with direct actions for reload, mapping configuration, and runtime refresh
- the web client keeps the backend contract stable during local development by using a proxy-friendly API base URL convention
- frontend lint, test, and build scripts are established so later feature work can focus on real operator flows

## Main Relationships

- depends on `External Surfaces`
- reflects `Access Control` capabilities
- displays data from `Runtime Inspection`
- triggers actions through `Lifecycle Orchestration`
- consumes AI proposal workflows from `AI Assistance Adapter`
