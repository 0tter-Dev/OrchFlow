# Project Registry

## Purpose

This module defines how projects are registered, identified, owned, and stored within OrchFlow.

## Objective

Provide a normalized internal project definition regardless of how a project was onboarded.

## Current Status

`implemented`

## Supported Registration Paths

### Existing Lifecycle Script

The user selects an existing `.bat` file that already defines lifecycle control.

For the current Windows batch adapter, registration validates that the selected script can be controlled through first-argument command dispatch, such as `control.bat STATUS`. Each canonical lifecycle action must resolve to a dispatch identifier either through the preferred default labels or through user-defined action mappings.

The registry now compares every newly connected `.bat` script against the ideal lifecycle function model. Preferred identifiers are mapped automatically during registration. Missing functions are represented as `undefined` in derived project responses, and users can map them manually or explicitly mark them as `unconfigured` through API and CLI workflows.

Registered projects can now be updated through non-AI API and CLI workflows. Users may change the project reference name, description, project root path, lifecycle script path, and lifecycle mappings. Updates reuse the same `.bat` path validation, first-argument dispatch checks, duplicate reference-name protection, and lifecycle mapping validation used by registration and manual configuration workflows. If an update changes the script path without explicit mappings, OrchFlow reloads compatible existing decisions against the new script so imported mappings can refresh while valid user-defined and AI-approved decisions remain preferred when their handlers still exist.

Users can explicitly reload one project or multiple projects in sequence after local `.bat` or project changes. Reload rereads the lifecycle script, refreshes imported preferred-identifier mappings, preserves valid user-defined or AI-approved mappings when the script still exposes their handlers, keeps explicit `unconfigured` decisions, returns the previous and current configuration health, reports changed actions, and writes an audit event.

Projects with at least one `configured` lifecycle function can be registered or manually reconfigured. Projects where every ideal lifecycle function is `undefined` or `unconfigured` are treated as not operationally controllable until at least one function is configured.

### AI-Assisted Script Creation

The user selects a project folder, OrchFlow analyzes it through the LiteLLM-backed `AI Assistance Adapter`, and the user reviews a suggested `.bat` lifecycle script before registration.

## Key Rules

- every project must end with a concrete `.bat` lifecycle script
- each project must have a user-facing reference name
- project metadata and lifecycle script paths may be updated only through validated registry workflows
- registration must persist ownership and permission metadata
- admins may assign or remove project owners
- project ownership changes must be auditable
- a project must retain at least one owner
- the registry should normalize onboarding inputs into a common internal project definition
- project connection details should be represented through a generic `Project Adapter` contract
- project-specific lifecycle action mappings must be persistable when canonical labels are not used
- lifecycle function configuration state is now partially persisted so OrchFlow can distinguish automatic detection, missing information, and explicit unconfigured user decisions
- automatic script analysis may mark functions as `configured` or `undefined`, but only a user action may mark a function as `unconfigured`
- partially configured projects should remain usable and should present warnings plus manual and AI-assisted improvement paths
- projects with no configured lifecycle function should be blocked from operational use until at least one function is mapped
- users should be able to explicitly reload one project or multiple projects to refresh script analysis and mapping guidance after local `.bat` or project changes
- users should be able to update registered project metadata, lifecycle script paths, and action mappings without AI assistance while preserving validation and auditability
- existing `.bat` registration must validate first-argument dispatch compatibility before persisting the project definition
- scripts that define labels or menus but do not dispatch from `%~1` or `%1` should be rejected with actionable operator-facing guidance
- AI-generated script proposals must not be persisted without user review
- the first concrete registration flow may focus on existing `.bat` files before AI-assisted onboarding is introduced

## Main Relationships

- depends on `Access Control` for ownership and visibility
- depends on `Lifecycle Script Template` for contract expectations
- provides definitions to `Lifecycle Orchestration`
- provides adapter-ready data to `Project Adapter`
- may receive assistance from `AI Assistance Adapter`
- persists through `Persistence And Audit`
