# Project Adapter

## Purpose

This module defines the generic adapter layer used to connect OrchFlow to managed projects.

## Objective

Ensure OrchFlow can interact with many different projects through a stable internal contract instead of coupling lifecycle logic to one specific project structure.

## Current Status

`implemented`

## Responsibilities

- interpret normalized project definitions
- resolve the effective lifecycle script location
- prepare the execution context for a project
- expose project-specific runtime interaction through a generic internal contract
- isolate project-specific operational details from the core application layer
- normalize project-specific action names into OrchFlow canonical lifecycle actions

## Canonical Action Mapping

OrchFlow should treat these lifecycle actions as canonical:

- `status`
- `start`
- `stop`
- `restart`

Each managed project may map those canonical actions to script-specific labels or command identifiers.

Examples:

- `start -> START`
- `start -> INICIAR`
- `stop -> PARAR`
- `status -> VERIFICAR`

## Mapping Configuration

The user should be able to configure action mappings case by case when a script does not follow the preferred label names.

This mapping should be stored as part of the project integration definition and should retain audit metadata such as:

- which user configured the mapping
- when the mapping was created
- when it was last updated
- whether the mapping was user-defined, imported, or AI-suggested and later approved

## Persistence Direction

Action mappings should be persisted per project and associated with the responsible user action so OrchFlow can consistently execute the correct script behavior later.

## Current Dispatch Contract

The current Windows batch adapter executes lifecycle actions by calling the registered script with one command identifier argument:

```text
control.bat ACTION_IDENTIFIER
```

By default, OrchFlow resolves canonical actions to uppercase identifiers such as `STATUS`, `START`, `STOP`, and `RESTART`. When a project uses different identifiers, user-defined mappings such as `start -> INICIAR` determine the identifier passed to the script.

Project registration validates that every effective identifier is represented by a first-argument dispatch handler before the project is persisted.

## Key Rules

- OrchFlow must not encode one-off project logic directly into the core
- the adapter must remain project-agnostic and configuration-driven
- the adapter should support different projects without changing the domain model
- the adapter must treat the lifecycle `.bat` file as the operational authority in `v0.2.0`
- OrchFlow should always target canonical lifecycle actions internally, even when external scripts use different names
- mapping flexibility must not weaken auditability or traceability
- the first concrete adapter path may assume command-dispatch by argument for `.bat` execution, and this assumption should remain explicit until broader script compatibility is added

## Main Relationships

- receives project data from `Project Registry`
- is used by `Lifecycle Orchestration`
- should follow the `Lifecycle Script Template` expectations
- may provide metadata for `Runtime Inspection`
- depends on `Persistence And Audit` for stored action mappings
