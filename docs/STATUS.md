# Feature Status

## Purpose

This document tracks the current implementation state of major OrchFlow capabilities.

## Legend

- `planned`: defined in documentation but not started
- `in_progress`: currently being implemented
- `implemented`: available in the product
- `review_needed`: present but requires design or behavior review

## Current Project Stage

OrchFlow is currently in the `v0.2.0` implementation stage as of `2026-08-24`.

## Feature Table

| Feature | Purpose | Status | Notes |
| --- | --- | --- | --- |
| Project architecture | Define scope, rules, constraints, and goals | implemented | Initial documentation baseline created |
| Development guide | Define engineering and architectural discipline | implemented | Initial standards established |
| User guide | Explain the intended usage flow | implemented | First example workflow documented |
| To-do roadmap | Track next planned project steps | implemented | Current implementation roadmap documented and kept focused on upcoming work |
| Agent rules | Constrain AI-assisted project changes | implemented | `AGENTS.md` created |
| Python project metadata | Define the backend package and toolchain baseline | implemented | `uv` and `pyproject.toml` initialized |
| Frontend package manager decision | Define the JavaScript package manager baseline for the web client | implemented | `pnpm` selected for the `interface/web` direction |
| Repository standards | Define ignore rules, line endings, editor behavior, and license | implemented | Git foundation files created |
| Configuration contract | Define runtime configuration and `.env` direction | in_progress | Validated settings loading and path normalization are implemented; further feature-specific config still pending |
| Access control | Authenticate users and enforce permissions | implemented | Bootstrap admin creation, JWT login, current-user resolution, admin listing, user role/activation updates, last-active-admin protection, and audit logging are implemented |
| Project registry | Register and persist project definitions | implemented | Existing `.bat` registration, ownership persistence and management, normalized action mappings, and first-argument dispatch validation are implemented |
| Project adapter | Connect OrchFlow to managed projects through a generic adapter boundary | implemented | Windows `.bat` command-dispatch adapter with canonical action mapping resolution is implemented |
| Lifecycle script template | Define the standard `.bat` contract used by managed projects | implemented | Includes minimum actions and a concrete reference-based example |
| Lifecycle orchestration | Run `status`, `start`, `stop`, `restart` | implemented | First practical execution flow with auditable results exposed in API and CLI is implemented |
| Runtime inspection | Inspect ports, PID, CPU, memory, uptime | implemented | Windows-local inspection baseline with port, URL, PID, uptime, CPU, and memory summaries is exposed in API and CLI |
| AI agent adapter | Analyze project folders and help generate `.bat` scripts | planned | Optional, mediated, review-driven, and mapping-aware |
| CLI surface | Expose orchestration through terminal commands | in_progress | Authentication, project registry, lifecycle execution, runtime inspection, admin audit history, user management, and owner management are mirrored; broader operator workflows still pending |
| API surface | Expose orchestration through HTTP endpoints | in_progress | Authentication, project registry, lifecycle execution, runtime inspection, admin audit history, user management, and owner management are mirrored; broader operator workflows still pending |
| Interface layer | Visualize and control projects across client platforms | in_progress | `interface/web` includes authenticated session loading, project registration, project visibility, runtime inspection, lifecycle controls, admin audit history, user management, owner management, and a shared API client boundary |
| Persistence and audit | Store users, projects, permissions, events | implemented | SQLAlchemy engine/session bootstrap, Alembic migrations, users, audit events, projects, ownership, lifecycle action mappings, and admin history visibility are implemented |
| DevOps and CI | Enforce repository quality and automation | in_progress | Git and GitHub flow documented, including human-driven and agent-driven PR modes; PR and issue templates plus backend and frontend validation workflow created |

## Implementation Notes

- The initial project planning, documentation baseline, and repository skeleton were completed before the current implementation stage.
- The consolidated documentation model and Git plus GitHub workflow foundation were completed before the current implementation stage.
- The project is now operating in `v0.2.0`, which consolidates the first real backend and web implementation milestones on `main`.
- The initial backend bootstrap now exists with executable API and CLI entrypoints plus smoke tests.
- Configuration loading, runtime path normalization, SQLAlchemy bootstrap, and Alembic migrations are available as part of the current baseline.
- API and CLI should keep evolving as mirrored external surfaces whenever a capability is intentionally exposed to operators.
- Access control is now implemented at the foundation level with mirrored registration, login, current-user, admin listing, and admin user update flows in API and CLI.
- Project registry is now implemented for existing `.bat` onboarding, with ownership persistence and management, auditable lifecycle action mappings, and registration-time validation for first-argument dispatch compatibility exposed in both API and CLI.
- Lifecycle orchestration is now implemented with the first Windows batch execution flow using command-dispatch by argument and mirrored lifecycle actions in API and CLI.
- Runtime inspection is now implemented with a first Windows-local baseline that extracts script hints, inspects listening ports and process metadata, and mirrors the capability in API and CLI.
- Admin audit history visibility is now implemented through a shared application service and exposed as `GET /audit/events`, `orchflow audit events`, and the web audit panel for recent operational events.
- Admin and ownership management is now implemented through user role/activation updates, last-active-admin protection, project owner add/remove operations, and the first web admin management panel.
- The first practical web client flow now exists in `interface/web`, covering sign-in, existing `.bat` project registration, project listing, project details, runtime inspection visibility, lifecycle controls, admin audit history, user management, and owner management against the stabilized API contracts.
- The web client now uses a local proxy-friendly API base URL contract so frontend development can stay aligned with the backend surface without introducing special backend-only web behavior.
- The Git and GitHub maintenance flow is now documented.
- The Git and GitHub flow now documents both human-driven and agent-driven pull request authorship, while preserving human review and merge authority on protected branches.
- Pull request descriptions now explicitly use `.github/PULL_REQUEST_TEMPLATE.md` as the standard structure for reviewer-facing summaries, validation notes, and documentation checklists.
- Pull request and issue templates plus CI workflow coverage for backend and frontend validation have been added locally.
- The backend CI workflow now expects collected tests because the bootstrap stage includes smoke coverage, and the repository now also validates the new frontend bootstrap.
- The frontend package manager direction is now defined as `pnpm`.
- The repository workflow now supports both maintainer-authored and agent-authored pull requests with a dedicated repository identity and human-controlled review on `main`.
- Any implementation work should update this file as features move from `planned` to later states.
