# Project Registry

## Purpose

This module defines how projects are registered, identified, owned, and stored within OrchFlow.

## Objective

Provide a normalized internal project definition regardless of how a project was onboarded.

## Current Status

`planned`

## Supported Registration Paths

### Existing Lifecycle Script

The user selects an existing `.bat` file that already defines lifecycle control.

### AI-Assisted Script Creation

The user selects a project folder, OrchFlow analyzes it through the `AI Agent Adapter`, and the user reviews a suggested `.bat` lifecycle script before registration.

## Key Rules

- every project must end with a concrete `.bat` lifecycle script
- each project must have a user-facing reference name
- registration must persist ownership and permission metadata
- the registry should normalize onboarding inputs into a common internal project definition
- AI-generated script proposals must not be persisted without user review

## Main Relationships

- depends on `Access Control` for ownership and visibility
- provides definitions to `Lifecycle Orchestration`
- may receive assistance from `AI Agent Adapter`
- persists through `Persistence And Audit`
