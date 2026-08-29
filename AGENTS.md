# AGENTS.md

## Purpose

This file defines the operating rules for AI agents working on OrchFlow.

## Source Of Truth

Agents must treat the following documents as the primary source of truth, in this order:

1. `docs/PROJECT-ARCHITECTURE.md`
2. `docs/DEVELOPMENT-GUIDE.md`
3. `docs/INDEX.md`
4. `docs/STATUS.md`
5. `docs/USER-GUIDE.md`

Files inside `docs/context/` are feature-level context documents. AI agents must not read or rely on `docs/context/` by default before making changes. They may consult `docs/context/` only when the requesting user explicitly authorizes that access and the context file is within the scope of the requested action.

If an AI agent determines from `docs/INDEX.md`, `docs/STATUS.md`, or another root-level `docs/` document that more feature context may be needed, the agent must ask the requesting user for explicit authorization before reading the relevant file inside `docs/context/`.

If two documents appear to conflict, the Project Architecture and Development Guide take priority until the maintainers explicitly revise the documentation.

Before any alteration, AI agents must ground their understanding in the applicable root-level documentation under `docs/`. Documentation is the baseline for implementation decisions, not an optional post-change check.

## Required Behavior

Agents must:

- preserve the local-first purpose of the project
- keep `.bat` lifecycle scripts as the concrete operational base for managed projects in `v0.2.14`
- preserve the ideal lifecycle function model as the reference for project mapping, configuration health, warnings, blocking rules, reload, and AI-assisted `.bat` improvement
- treat the AI assistance layer as optional assistance mediated by OrchFlow, not as the authoritative lifecycle controller
- treat `LiteLLM` as the planned central LLM/model gateway, while keeping OrchFlow responsible for allowed context, file access, review-driven flow, validation, and final user approval
- respect the documented scope, non-goals, and architectural boundaries
- prefer small, explicit, reviewable changes
- keep documentation and implementation aligned
- update all relevant documentation when meaningful implementation work is performed, especially code changes
- after any relevant code change, re-evaluate the root-level documentation and any explicitly authorized, scope-relevant context documentation to update the documentation affected by the change
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
- the ideal lifecycle function model, function configuration states, or blocking semantics for projects with no configured lifecycle actions
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
- the relevant file in `docs/context/` only when the requesting user explicitly authorized consultation or update of that scope
- `docs/INDEX.md` if cross-feature relationships changed
- `docs/PROJECT-ARCHITECTURE.md` if business scope or policy changed
- `docs/TO-DO.md` when the planned next steps changed or previously planned work was completed

AI agents must not treat documentation updates as optional cleanup. If code behavior changes, the agent must actively verify whether the related documentation needs to change and either update it or state why no documentation update was required.

Every pull request must also evaluate and update the system version according to the change being proposed. Version updates must keep project metadata, runtime version exposure, tests, lockfiles, and documentation aligned with the semantic versioning guidance in `docs/GIT-GITHUB-FLOW.md` and `docs/DEVELOPMENT-GUIDE.md`.

## Code Delivery Workflow

For code-changing work such as a fix, chore, refactor, test change, or feature, AI agents must follow the documented Git and GitHub workflow in `docs/GIT-GITHUB-FLOW.md` when agent-driven delivery is enabled or explicitly requested.

The expected agent-driven delivery sequence is:

1. read the applicable root-level documentation under `docs/`
2. request explicit authorization before reading any needed `docs/context/` file
3. make the focused code and documentation changes
4. run the relevant local validation commands for the changed backend and/or frontend scope
5. inspect the resulting diff and working tree status
6. create a short-lived branch specific to the change
7. commit the validated change with an appropriate Conventional Commit message
8. push the branch to the remote repository
9. open a pull request into `main`

Agent-driven branch, commit, push, and pull request operations must use only `git` and `gh` through the CLI. Agents must not use GitHub web UI automation, remote GitHub write connectors, or hidden repository operations for this workflow.

Pull request descriptions must be created from the repository standard template at `.github/PULL_REQUEST_TEMPLATE.md`. When opening a pull request through `gh pr create`, agents must use that template as the description structure, fill the applicable sections, and preserve any checklist items that remain relevant to the change.

Every agent-authored pull request must explicitly mention the version bump decision in its description, including whether the PR changes the version and why that bump level is appropriate.

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
- bypass the OrchFlow AI assistance adapter by calling `LiteLLM` directly from CLI, API, UI, domain, or unrelated application services
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
