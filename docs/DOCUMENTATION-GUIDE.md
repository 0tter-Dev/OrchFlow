# Documentation Guide

## Purpose

This guide defines the OrchFlow documentation system. It supports readers with no prior project context without requiring oversized files or excessive traversal.

## Information Architecture

| Area | Owns | Does not own |
| --- | --- | --- |
| Root documents | product scope, engineering rules, status, roadmap, and reading routes | feature-level implementation narrative |
| `capabilities/` | canonical behavior, invariants, contracts, implementation evidence, and validation | temporary planning or durable cross-cutting rationale |
| `reference/` | stable contracts and definitions | procedural instructions |
| `guides/` | task-oriented instructions | canonical feature rules |
| `decisions/` | durable architecture and policy choices | normal implementation notes |
| `plans/` | approved future work and completed outcomes | current product behavior |

Each capability has one canonical `README.md`. Companion files exist only for independently large contracts.

## Status And Duplication Rules

`STATUS.md` is a compact dashboard. `ROADMAP.md` is a compact index. The root `README.md` is a concise public portal. Each links to its source instead of duplicating its full narrative.

## Plan Lifecycle And Context Authorization

Plans follow `backlog → active → review → completed`, with `cancelled` as an explicit terminal alternative. Plans move from `backlog` to `active` only after explicit user approval recorded in the plan body. `ROADMAP.md` is the canonical ordered queue: its `Sequence` column defines the default execution order, while each plan's `depends_on` field names hard prerequisites and `priority` describes urgency rather than execution order. Only the first eligible item may be activated unless the user explicitly authorizes parallel work or reordering. An active plan authorizes only the exact paths in `authorized_capabilities`; it never expands product scope or replaces approval required for architectural decisions.

Every new plan is a delivery plan and sets `requires_pull_request: true`. Preparation, research, documentation, or migration work that does not independently merit review is recorded as a phase, task, acceptance criterion, or validation item inside the delivery plan; it does not receive a separate lifecycle. The recorded approval authorizes the agent to complete the standard scoped delivery sequence — synchronized branch, implementation, validation, Conventional Commit, push, and pull request — without a second authorization for those Git actions. The plan moves to `review` in that PR and records its URL, delivery commit, validation, and `actual_version_impact`; only a merged PR permits transition to `completed`. Before activating an item, reconcile every `active` and `review` plan with GitHub and local `main`; `ROADMAP.md`, `STATUS.md`, plan directory, and front matter must agree.

## Decision Records

Use an ADR only for decisions that affect multiple capabilities, the architecture, strategic dependencies, or durable policy. ADRs record context, decision, consequences, alternatives, and canonical links.

## Maintenance

Keep internal Markdown links valid. Update the owning capability, guide, plan, or ADR with meaningful behavior and governance changes. The documentation structure contract test verifies topology and required plan metadata.
