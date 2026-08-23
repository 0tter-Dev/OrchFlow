# Feature Status

## Purpose

This document tracks the current implementation state of major OrchFlow capabilities.

## Legend

- `planned`: defined in documentation but not started
- `in_progress`: currently being implemented
- `implemented`: available in the product
- `review_needed`: present but requires design or behavior review

## Current Project Stage

OrchFlow is currently in the documentation foundation stage as of `2026-08-23`.

## Feature Table

| Feature | Purpose | Status | Notes |
| --- | --- | --- | --- |
| Project architecture | Define scope, rules, constraints, and goals | implemented | Initial documentation baseline created |
| Development guide | Define engineering and architectural discipline | implemented | Initial standards established |
| User guide | Explain the intended usage flow | implemented | First example workflow documented |
| To-do roadmap | Track next planned project steps | implemented | Initial planning backlog documented |
| Agent rules | Constrain AI-assisted project changes | implemented | `AGENTS.md` created |
| Access control | Authenticate users and enforce permissions | planned | Initial role model: `admin`, `member` |
| Project registry | Register and persist project definitions | planned | `.bat` is the lifecycle authority |
| Lifecycle orchestration | Run `status`, `start`, `stop`, `restart` | planned | Based on normalized project definitions |
| Runtime inspection | Inspect ports, PID, CPU, memory, uptime | planned | Local-first runtime inspection |
| AI agent adapter | Analyze project folders and help generate `.bat` scripts | planned | Optional, mediated, and review-driven |
| CLI surface | Expose orchestration through terminal commands | planned | Must mirror application use cases |
| API surface | Expose orchestration through HTTP endpoints | planned | Must mirror CLI capabilities |
| Interface layer | Visualize and control projects | planned | Depends on API contracts |
| Persistence and audit | Store users, projects, permissions, events | planned | Initial direction points to SQLite |
| DevOps and CI | Enforce repository quality and automation | planned | GitHub-oriented workflow expected |

## Implementation Notes

- No production source code has been created yet.
- Documentation currently defines the intended baseline for `v0.1.0`.
- The initial folder skeleton has been created without source code files.
- Any implementation work should update this file as features move from `planned` to later states.
