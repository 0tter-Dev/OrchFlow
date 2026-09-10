# ADR-0001: Local-First `.bat` Lifecycle Contract

## Context

OrchFlow manages local Windows projects and needs an explicit, reviewable execution contract.

## Decision

Keep Windows `.bat` lifecycle scripts as the authoritative managed-project contract in `v0.3.32`.

## Consequences

Lifecycle execution remains inspectable and project-specific behavior stays outside the core. Container, remote, and autonomous control are not introduced by this decision.

## Alternatives Considered

Direct framework-specific commands and AI-managed execution were rejected because they weaken the explicit local contract.

## Canonical Links

[Architecture](../PROJECT-ARCHITECTURE.md) and [Lifecycle Management](../capabilities/lifecycle-management/README.md).
