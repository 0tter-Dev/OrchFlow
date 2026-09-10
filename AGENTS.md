# AGENTS.md

## Purpose

These rules keep agent work aligned with OrchFlow's local-first architecture, documented decisions, and review-driven delivery model.

## Required Reading And Documentation Authority

Before changing the repository, read in this order:

1. `docs/PROJECT-ARCHITECTURE.md`
2. `docs/DEVELOPMENT-GUIDE.md`
3. `docs/DOCUMENTATION-GUIDE.md`
4. `docs/STATUS.md`
5. the relevant document in `docs/plans/active/`, when one exists

`docs/START-HERE.md` is the navigation entrypoint. The root documents establish scope and engineering policy; capability documents establish current feature behavior; reference documents establish stable contracts; guides establish procedures; ADRs establish durable rationale; and plans establish bounded intended work.

Agents must not read capability documents by default. An active plan authorizes only the exact repository-relative files listed in its `authorized_capabilities` metadata when the plan records explicit user approval. All other capability access requires explicit user authorization. An active plan never authorizes a product-scope, public-contract, architecture, dependency, authentication, or authorization change that independently requires approval.

## Required Behavior

Agents must preserve the local-first purpose, Windows `.bat` lifecycle contract, ideal lifecycle function model, review-driven optional AI layer, LiteLLM adapter boundary, and documentation-code alignment. Prefer small, explicit, auditable changes. Keep `ROADMAP.md` as an index and place detailed future work in `docs/plans/backlog/`.

After relevant code changes, update the owning capability and all affected status, guide, reference, decision, or plan documents. Completed plans move to `docs/plans/completed/` with outcome, validation, version decision, commit, and pull request references when applicable.

## Scope Boundaries

Agents may change implementation details within the documented architecture; tests and behavior-preserving refactors; and documentation clarity. Explicit approval is required for changes to the `.bat` lifecycle authority, lifecycle configuration semantics, architecture, persistence assumptions, authentication or authorization semantics, public APIs, strategic dependencies, stack direction, or local-first scope.

## Implementation Discipline

Follow clean architecture pragmatically. Keep business rules out of delivery adapters, avoid dead code and speculative abstractions, favor explicit contracts, and document durable decisions through ADRs when they affect multiple capabilities or product policy.

## Git And Delivery

For Roadmap work, verify remote `main`, synchronize local `main`, and create a short-lived branch from that baseline before implementation. Agent Git actions require explicit user authorization or an explicitly enabled agent-driven workflow. Use only `git` and `gh`, the repository-specific identity `0tter-Dev-AI <otter.dev.ai@gmail.com>` unless replaced by maintainers, Conventional Commits, the PR template, version-decision discipline, validation, push, and a PR into `main`. Never merge an agent-authored PR.

## Safety Rules

Do not bypass permissions, make AI output authoritative, call LiteLLM outside the OrchFlow adapter, silently redefine the mission, delete managed project folders or lifecycle scripts through unlinking, or weaken the documentation-first workflow.
