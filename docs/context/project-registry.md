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

### AI-Assisted Script Creation

The user selects a project folder, OrchFlow analyzes it through the LiteLLM-backed `AI Assistance Adapter`, and the user reviews a suggested `.bat` lifecycle script before registration.

## Key Rules

- every project must end with a concrete `.bat` lifecycle script
- each project must have a user-facing reference name
- registration must persist ownership and permission metadata
- admins may assign or remove project owners
- project ownership changes must be auditable
- a project must retain at least one owner
- the registry should normalize onboarding inputs into a common internal project definition
- project connection details should be represented through a generic `Project Adapter` contract
- project-specific lifecycle action mappings must be persistable when canonical labels are not used
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
