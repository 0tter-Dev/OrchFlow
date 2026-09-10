# ADR-0003: LiteLLM Through The OrchFlow AI Adapter

## Context

AI assistance must be useful without gaining authority over project files or lifecycle execution.

## Decision

Use LiteLLM only behind the OrchFlow AI assistance adapter, with authorized context manifests, reviewable proposals, validation, and separately confirmed application.

## Consequences

Provider connectivity can evolve while OrchFlow retains authorization, auditability, and final approval.

## Alternatives Considered

Direct provider calls from CLI, API, UI, or domain code were rejected.

## Canonical Links

[AI Assistance](../capabilities/ai-assistance/README.md).
