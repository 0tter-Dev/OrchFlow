# Roadmap

## Purpose

This is the canonical ordered queue of planned OrchFlow work. Detailed scope, authorized capability context, validation, version impact, and delivery intent belong in individual plan documents.

## Execution Rules

`Sequence` defines the default execution order. `Priority` expresses urgency and does not override that order. `Dependencies` lists hard prerequisites only; `—` means none. A plan becomes eligible only when its dependencies are completed and every earlier Roadmap item is reconciled. By default, only the first eligible plan may move to `active`; parallel work or reordering requires explicit user approval and a documented Roadmap update.

Every listed item is one delivery plan and results in one pull request. Research, preparation, documentation, or migration work that does not independently merit review stays as a phase, task, acceptance criterion, or validation item inside its delivery plan rather than becoming a separate plan.

## Active Plans

No plan is currently active.

## Plans Awaiting Review

| Sequence | Plan | Priority | Dependencies |
| --- | --- | --- | --- |
| 11 | [web-014: ESLint toolchain migration](./plans/review/web-014-eslint-toolchain-migration.md) | medium | deps-001 |

## Backlog

| Sequence | Plan | Priority | Dependencies |
| --- | --- | --- | --- |

The listed plans are backlog candidates. They do not authorize implementation, dependency installation, capability access, public API changes, or product-scope changes until explicitly approved and moved to `plans/active/`.

## Completed Plans

See [deps-003 Node.js and Corepack runtime support](./plans/completed/deps-003-node-corepack-runtime-support.md), [deps-002 pnpm 12 migration](./plans/completed/deps-002-pnpm-12-migration.md), [deps-001 central dependency maintenance assessment](./plans/completed/deps-001-central-dependency-maintenance-assessment.md), [web-012 critical browser workflow tests](./plans/completed/web-012-critical-browser-workflow-tests.md), [web-011 workspace internationalization](./plans/completed/web-011-workspace-internationalization.md), [web-010 advanced operational tables](./plans/completed/web-010-advanced-operational-tables.md), [web-009 accessible operational feedback](./plans/completed/web-009-accessible-operational-feedback.md), [web-008 guided project forms](./plans/completed/web-008-guided-project-forms.md), [web-007 local path-selection workflow](./plans/completed/web-007-local-path-selection-workflow.md), [web-006 local path-selection contract](./plans/completed/web-006-local-path-selection-contract.md), [web-005 focused project workspace flows](./plans/completed/web-005-focused-project-workspace-flows.md), [web-004 API-backed workspace state](./plans/completed/web-004-api-backed-workspace-state.md), [web-003 authenticated workspace navigation](./plans/completed/web-003-authenticated-workspace-navigation.md), [web-002 React runtime compatibility update](./plans/completed/web-002-react-runtime-compatibility-update.md), [web-001 compatible web dependency maintenance](./plans/completed/web-001-compatible-web-dependency-maintenance.md), and [documentation governance modularization](./plans/completed/docs-001-documentation-governance.md). Historical work completed before this documentation model remains traceable through Git history, releases, and [Feature Status](./STATUS.md).
