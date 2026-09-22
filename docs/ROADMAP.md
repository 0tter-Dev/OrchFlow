# Roadmap

## Purpose

This is the canonical ordered queue of planned OrchFlow work. Detailed scope, authorized capability context, validation, version impact, and delivery intent belong in individual plan documents.

## Execution Rules

`Sequence` defines the default execution order. `Priority` expresses urgency and does not override that order. `Dependencies` lists hard prerequisites only; `—` means none. A plan becomes eligible only when its dependencies are completed and every earlier Roadmap item is reconciled. By default, only the first eligible plan may move to `active`; parallel work or reordering requires explicit user approval and a documented Roadmap update.

Every listed item is one delivery plan and results in one pull request. Research, preparation, documentation, or migration work that does not independently merit review stays as a phase, task, acceptance criterion, or validation item inside its delivery plan rather than becoming a separate plan.

## Active Plans

| Sequence | Plan | Priority | Dependencies |
| --- | --- | --- | --- |
| 19 | [web-020: user visual preferences](./plans/active/web-020-user-visual-preferences.md) | medium | `web-019` |

## Backlog

| Sequence | Plan | Priority | Dependencies |
| --- | --- | --- | --- |
| 20 | [web-021: operational workspace hierarchy](./plans/backlog/web-021-operational-workspace-hierarchy.md) | medium | `web-020` |
| 21 | [web-022: reusable visual system](./plans/backlog/web-022-reusable-visual-system.md) | medium | `web-021` |
| 22 | [web-023: desktop UX and accessibility audit](./plans/backlog/web-023-desktop-ux-accessibility-audit.md) | medium | `web-022` |
| 23 | [web-024: profile and preferences refinement](./plans/backlog/web-024-profile-preferences-refinement.md) | low | `web-023` |

The listed plans are backlog candidates. They do not authorize implementation, dependency installation, capability access, public API changes, or product-scope changes until explicitly approved and moved to `plans/active/`.

## Completed Plans

Completed delivery records, including their outcomes, validation, version decisions, commits, and pull requests, are stored in [plans/completed](./plans/completed/). Historical work completed before this documentation model remains traceable through Git history, releases, and [Feature Status](./STATUS.md).
