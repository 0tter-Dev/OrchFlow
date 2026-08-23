# Feature Status

## Purpose

This document tracks the current implementation state of major OrchFlow capabilities.

## Legend

- `planned`: defined in documentation but not started
- `in_progress`: currently being implemented
- `implemented`: available in the product
- `review_needed`: present but requires design or behavior review

## Current Project Stage

OrchFlow is currently in the repository foundation stage as of `2026-08-23`.

## Feature Table

| Feature | Purpose | Status | Notes |
| --- | --- | --- | --- |
| Project architecture | Define scope, rules, constraints, and goals | implemented | Initial documentation baseline created |
| Development guide | Define engineering and architectural discipline | implemented | Initial standards established |
| User guide | Explain the intended usage flow | implemented | First example workflow documented |
| To-do roadmap | Track next planned project steps | implemented | Initial planning backlog documented |
| Agent rules | Constrain AI-assisted project changes | implemented | `AGENTS.md` created |
| Python project metadata | Define the backend package and toolchain baseline | implemented | `uv` and `pyproject.toml` initialized |
| Repository standards | Define ignore rules, line endings, editor behavior, and license | implemented | Git foundation files created |
| Configuration contract | Define runtime configuration and `.env` direction | implemented | `.env.example` provides the initial local contract |
| Access control | Authenticate users and enforce permissions | planned | Initial role model: `admin`, `member` |
| Project registry | Register and persist project definitions | planned | `.bat` is the lifecycle authority |
| Project adapter | Connect OrchFlow to managed projects through a generic adapter boundary | planned | Must remain project-agnostic and support action mapping |
| Lifecycle script template | Define the standard `.bat` contract used by managed projects | implemented | Includes minimum actions and a concrete reference-based example |
| Lifecycle orchestration | Run `status`, `start`, `stop`, `restart` | planned | Based on normalized project definitions |
| Runtime inspection | Inspect ports, PID, CPU, memory, uptime | planned | Local-first runtime inspection |
| AI agent adapter | Analyze project folders and help generate `.bat` scripts | planned | Optional, mediated, review-driven, and mapping-aware |
| CLI surface | Expose orchestration through terminal commands | planned | Must mirror application use cases |
| API surface | Expose orchestration through HTTP endpoints | planned | Must mirror CLI capabilities |
| Interface layer | Visualize and control projects across client platforms | planned | Interface clients must consume API contracts |
| Persistence and audit | Store users, projects, permissions, events | planned | Initial direction points to SQLite |
| DevOps and CI | Enforce repository quality and automation | in_progress | Git and GitHub flow documented; PR and issue templates plus initial CI workflow created |

## Implementation Notes

- No application implementation has been created yet.
- Documentation and repository standards currently define the intended baseline for `v0.1.0`.
- The initial folder skeleton has been created without feature code files.
- The Git and GitHub maintenance flow is now documented.
- Pull request and issue templates plus an initial backend CI workflow have been added locally.
- The initial CI workflow tolerates `pytest` exit code `5` while the repository still has no collected tests in the foundation stage.
- Branch protection and remote GitHub enforcement still need to be configured manually in the remote repository.
- Any implementation work should update this file as features move from `planned` to later states.
