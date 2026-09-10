# ADR-0002: Lifecycle Function Configuration Model

## Context

Existing scripts vary in supported actions and identifiers.

## Decision

Model each ideal lifecycle function as `configured`, `undefined`, or `unconfigured`; allow partial projects to execute only configured actions and block projects with none.

## Consequences

Operators receive explicit readiness guidance without assuming labels or silently executing unavailable operations.

## Alternatives Considered

Requiring all four functions and assuming canonical labels were rejected because they unnecessarily exclude existing local projects.

## Canonical Links

[Lifecycle Management](../capabilities/lifecycle-management/README.md) and [Script Contract](../capabilities/lifecycle-management/script-contract.md).
