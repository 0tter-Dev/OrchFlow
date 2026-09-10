# ADR-0004: Local SQLite And Ownership Authorization

## Context

The local-first baseline needs persistence and authorization without remote infrastructure.

## Decision

Use SQLite with SQLAlchemy and Alembic, and authorize project access through `admin` role or explicit ownership assignments.

## Consequences

Local operation stays lightweight while auditability, migrations, and explicit ownership remain available.

## Alternatives Considered

Remote-first persistence and a generic permission table were deferred.

## Canonical Links

[Persistence And Audit](../capabilities/persistence-and-audit/README.md) and [Access Control](../capabilities/access-control/README.md).
