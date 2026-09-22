# AGENTS.md

## Purpose

These rules keep agent work aligned with OrchFlow's local-first architecture, documented decisions, and review-driven delivery model.

## Required Reading And Documentation Authority

Before changing the repository, read in this order:

1. `docs/PROJECT-ARCHITECTURE.md`
2. `docs/DEVELOPMENT-GUIDE.md`
3. `docs/DOCUMENTATION-GUIDE.md`
4. `docs/STATUS.md`
5. the relevant document in `docs/plans/active/` or `docs/plans/review/`, when one exists

`docs/START-HERE.md` is the navigation entrypoint. The root documents establish scope and engineering policy; capability documents establish current feature behavior; reference documents establish stable contracts; guides establish procedures; ADRs establish durable rationale; and plans establish bounded intended work.

Agents must not read capability documents by default. An active plan authorizes only the exact repository-relative files listed in its `authorized_capabilities` metadata when the plan records explicit user approval. All other capability access requires explicit user authorization. An active plan never authorizes a product-scope, public-contract, architecture, dependency, authentication, or authorization change that independently requires approval.

An active plan is operationally approved only when its body records the user's explicit approval. Every new delivery plan must set `requires_pull_request: true`; work too small to warrant an independent pull request belongs as a phase or acceptance criterion within its parent delivery plan, not as a separate plan. For an approved delivery plan, that field is explicit authorization to perform the documented delivery sequence only: create the branch from synchronized `main`, make the scoped changes, validate them, commit, push, and open the pull request. Do not request a second authorization solely for those standard delivery actions.

## Required Behavior

Agents must preserve the local-first purpose, Windows `.bat` lifecycle contract, ideal lifecycle function model, review-driven optional AI layer, LiteLLM adapter boundary, and documentation-code alignment. Prefer small, explicit, auditable changes. Keep `ROADMAP.md` as an index and place detailed future work in `docs/plans/backlog/`.

After relevant code changes, update the owning capability and all affected status, guide, reference, decision, or plan documents. A delivery plan moves from `active` to `review` in the same delivery PR once its validated commit is pushed and the PR is open. It moves to `completed` only after that PR is merged and local `main` is synchronized. Plans transitioned under this policy record outcome, validation, expected and actual version decision, commit, and PR references when completed.

## Continuous Roadmap Delivery

When a user approves an eligible Roadmap plan, execute its entire delivery sequence as one continuous task: reconcile GitHub and local `main`; synchronize `main`; create the branch; implement the approved scope; update documentation; run and repair validation; inspect the diff; commit; push; open the pull request; and move the plan to `review` with delivery metadata.

Do not end a turn, request routine confirmation, or wait for user input between those ordinary steps. Tool output, successful checks, routine test or lint failures, and in-scope implementation decisions are progress signals to resolve, not stopping points. Commentary is progress-only and never means delivery completion.

Stop only for a missing approval at a documented boundary, a clear security or data-loss risk, an external dependency that cannot be resolved safely, or a user request that supersedes the active plan.

## Scope Boundaries

Agents may change implementation details within the documented architecture; tests and behavior-preserving refactors; and documentation clarity. Explicit approval is required for changes to the `.bat` lifecycle authority, lifecycle configuration semantics, architecture, persistence assumptions, authentication or authorization semantics, public APIs, strategic dependencies, stack direction, or local-first scope.

## Implementation Discipline

Follow clean architecture pragmatically. Keep business rules out of delivery adapters, avoid dead code and speculative abstractions, favor explicit contracts, and document durable decisions through ADRs when they affect multiple capabilities or product policy.

## Git And Delivery

For Roadmap work, first reconcile every `active` and `review` plan against GitHub and local `main`. `docs/ROADMAP.md` defines the default execution sequence; only its first eligible item may move to `active` unless the user explicitly approves parallel work or a reordered sequence. An item is eligible only when its declared `depends_on` plans are completed and no earlier item is unreconciled. Then synchronize `main` and create the short-lived branch. A user-approved active plan explicitly enables the scoped agent-driven workflow; other Git actions still require explicit user authorization. Use only `git` and `gh`, the repository-specific identity `0tter-Dev-AI <otter.dev.ai@gmail.com>` unless replaced by maintainers, Conventional Commits, the PR template, version-decision discipline, validation, push, and a PR into `main`. Never merge an agent-authored PR.

## Safety Rules

Do not bypass permissions, make AI output authoritative, call LiteLLM outside the OrchFlow adapter, silently redefine the mission, delete managed project folders or lifecycle scripts through unlinking, or weaken the documentation-first workflow.
