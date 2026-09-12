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

Plans move from `backlog` to `active` only after explicit user approval recorded in the plan body. An active plan authorizes only the exact paths in `authorized_capabilities`; it never expands product scope or replaces approval required for architectural decisions.

`requires_pull_request` defines the delivery obligation of an approved active plan. When it is `true`, the recorded approval authorizes the agent to complete the standard scoped delivery sequence — synchronized branch, implementation, validation, Conventional Commit, push, and pull request — without a second authorization for those Git actions. The plan remains active until that pull request exists. When it is `false`, no pull request is created unless the user separately requests one. Completed plans retain their outcome, validation, version decision, commit, and pull request references when applicable.

## Decision Records

Use an ADR only for decisions that affect multiple capabilities, the architecture, strategic dependencies, or durable policy. ADRs record context, decision, consequences, alternatives, and canonical links.

## Maintenance

Keep internal Markdown links valid. Update the owning capability, guide, plan, or ADR with meaningful behavior and governance changes. The documentation structure contract test verifies topology and required plan metadata.
