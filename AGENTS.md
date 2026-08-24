# AGENTS.md

## Purpose

This file defines the operating rules for AI agents working on OrchFlow.

## Source Of Truth

Agents must treat the following documents as the primary source of truth, in this order:

1. `docs/PROJECT-ARCHITECTURE.md`
2. `docs/DEVELOPMENT-GUIDE.md`
3. `docs/INDEX.md`
4. Relevant files inside `docs/context/`
5. `docs/STATUS.md`
6. `docs/USER-GUIDE.md`

If two documents appear to conflict, the Project Architecture and Development Guide take priority until the maintainers explicitly revise the documentation.

## Required Behavior

Agents must:

- preserve the local-first purpose of the project
- keep `.bat` lifecycle scripts as the concrete operational base for managed projects in `v0.1.2`
- treat the `AI Agent Adapter` as optional assistance, not as the authoritative lifecycle controller
- respect the documented scope, non-goals, and architectural boundaries
- prefer small, explicit, reviewable changes
- keep documentation and implementation aligned
- update all relevant documentation when meaningful implementation work is performed, especially code changes
- keep `docs/TO-DO.md` limited to upcoming planned steps instead of retaining items that are already implemented
- avoid placeholder shared abstractions or generic kernel layers unless they serve a clear current purpose
- follow the documented repository workflow for human-driven and agent-driven pull request delivery
- avoid hidden architectural drift

## Scope Boundaries

Agents may change without explicit approval:

- implementation details that stay inside the documented architecture
- tests, validation logic, and refactoring that preserve behavior
- documentation updates that improve clarity without changing project policy
- internal code organization that does not alter product scope or architectural direction

Agents must request explicit approval before changing:

- the core execution contract based on `.bat` lifecycle scripts
- architectural style or major project structure
- persistence strategy in a way that materially changes operational assumptions
- authentication or authorization model semantics
- public API contracts
- framework selection when it introduces new strategic coupling
- major dependency additions or removals
- stack changes affecting the whole system
- product scope in ways that introduce container orchestration, remote orchestration, or non-local-first behavior
- established business rules, selected stack decisions, non-goals, or other core product-foundation rules already documented as part of the baseline

## Implementation Discipline

Agents must:

- follow SOLID and clean architecture principles where practical
- avoid dead code, speculative abstractions, and hidden side effects
- keep business rules out of delivery adapters such as CLI, API, and UI layers
- document significant decisions when they affect architecture or behavior
- favor explicit contracts over implicit conventions

## Documentation Discipline

When introducing or changing features, agents should update:

- `docs/STATUS.md` for implementation state
- the relevant file in `docs/context/`
- `docs/INDEX.md` if cross-feature relationships changed
- `docs/PROJECT-ARCHITECTURE.md` if business scope or policy changed
- `docs/TO-DO.md` when the planned next steps changed or previously planned work was completed

## Naming Discipline

Agents should prefer `kebab-case` for new free-form file and directory names.

Agents must preserve externally required names when a platform, framework, language, or repository convention depends on them.

Examples include:

- `.github/ISSUE_TEMPLATE/`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/ISSUE_TEMPLATE/config.yml`
- Python dunder files such as `__init__.py`
- standard dotfiles such as `.gitignore`

## Safety Rules

Agents must not:

- silently redefine the project mission
- bypass documented permissions rules
- introduce autonomous AI control over project lifecycle actions without explicit approval
- treat generated analysis as verified runtime truth
- erase or weaken the documentation-first workflow without authorization
- run Git commands such as `git add`, `git commit`, `git pull`, `git push`, `git merge`, `git rebase`, or remote GitHub write operations unless the user explicitly requests that action or has explicitly enabled the documented agent-driven Git workflow for the repository
- use the machine-global Git identity when operating in an agent-driven Git workflow if a repository-specific identity has been documented or configured for OrchFlow

When Git actions are needed but were not explicitly requested, agents should explain the required commands and let the user run them manually.

When the documented agent-driven Git workflow is enabled, agents must:

- use short-lived branches and pull requests exactly as defined in `docs/GIT-GITHUB-FLOW.md`
- use the repository-specific Git identity configured for OrchFlow instead of the machine-global identity
- avoid merging their own pull requests
- leave final review and merge authority to a human maintainer with repository admin access
