# Git And GitHub Flow

## Purpose

This document defines the standard Git and GitHub workflow for maintaining, extending, reviewing, and releasing OrchFlow.

## Objective

Create a disciplined and lightweight delivery flow that keeps the repository stable while the product moves from documentation foundation into real implementation.

## Core Principles

- keep `main` stable and reviewable
- prefer short-lived branches
- keep pull requests small and focused
- evolve documentation, tests, and implementation together
- use GitHub as the collaboration and review hub
- use semantic versioning consistently
- add CI quality gates before introducing full CD automation

## Workflow Model

OrchFlow should use a simplified GitHub Flow model.

This means:

- `main` is the primary protected branch
- all work starts from `main`
- all changes return through pull requests
- no direct pushes should be allowed to `main`
- branches should be deleted after merge
- work may be authored either by a human contributor or by an authorized AI agent using a dedicated repository identity

This project should not adopt a heavy Git Flow model in `v0.3.2`.

The repository is still in an early product stage, so a simpler branch model reduces process weight and makes maintenance easier.

## Branch Strategy

### Primary Branch

- `main`

Rules:

- always releasable
- protected in GitHub
- updated only through reviewed pull requests

### Working Branches

Every implementation, documentation, test, refactor, or CI task should use a short-lived branch created from `main`.

Recommended naming patterns:

- `feat/<short-scope>`
- `fix/<short-scope>`
- `docs/<short-scope>`
- `refactor/<short-scope>`
- `test/<short-scope>`
- `ci/<short-scope>`
- `chore/<short-scope>`

Examples:

- `docs/git-github-flow`
- `ci/backend-validation`
- `feat/project-registry-foundation`
- `test/lifecycle-contracts`

### Future Release Branches

Release branches are not part of the default workflow for the current stage.

They should only be introduced later if OrchFlow needs:

- parallel stabilization work
- simultaneous maintenance of multiple supported versions
- a formal pre-release hardening window

If that becomes necessary, the recommended format is:

- `release/<version>`

Example:

- `release/0.3.0`

### Future Hotfix Branches

If a critical correction is needed after releases become more formal, hotfix branches may be created from `main`.

Recommended format:

- `hotfix/<short-scope>`

This is a future exception flow, not the normal path for current development.

## Change Unit Discipline

Each branch should solve one coherent problem.

Good examples:

- define a backend bootstrap structure
- add authentication domain contracts
- create the initial CI workflow
- update documentation for lifecycle script registration

Avoid mixing unrelated concerns such as:

- API implementation plus unrelated UI design
- authentication changes plus repository tooling refactors
- runtime inspection logic plus release process changes

## Pull Request Flow

The expected lifecycle for each change is:

1. define or confirm the scope through an issue, roadmap item, or explicit task
2. create a short-lived branch from `main`
3. implement the focused change
4. update tests and documentation as needed
5. validate locally before opening the pull request
6. open a pull request into `main`
7. pass CI checks
8. receive at least one review
9. merge with squash merge
10. delete the branch

For agent-driven code changes, the agent must complete the local implementation, documentation alignment, validation, diff review, branch creation, commit, push, and pull request creation itself when the user has explicitly enabled or requested that delivery mode. The pull request remains the handoff point for human review and merge.

## Contributor Modes

OrchFlow supports two compatible delivery modes:

- human-driven pull requests, where the contributor authors the branch, commit, and pull request directly
- agent-driven pull requests, where an authorized AI agent performs the Git work on behalf of the repository using a dedicated repository identity

Both modes must follow the same protected-branch, validation, documentation, and review requirements.

## Agent-Driven Pull Request Rules

When agent-driven delivery is enabled for this repository:

- the agent may create branches, commit changes, push branches, and open pull requests
- the agent must use only `git` and `gh` through the CLI for branch, commit, push, and pull request operations
- the agent must not use GitHub web UI automation, remote GitHub write connectors, or hidden repository operations for this workflow
- the agent must not merge its own pull requests
- final review and merge authority must remain with a human maintainer who has repository admin access
- the agent should use a dedicated repository identity instead of the machine-global Git identity
- the agent should prefer one dedicated identity for the repository so PR authorship remains clear and auditable
- the repository should document that identity policy in `AGENTS.md`

This model is especially useful when the repository owner is the only human reviewer but still wants agent-authored pull requests that can be reviewed from the maintainer account.

## Pull Request Rules

Every pull request should:

- target `main`
- solve one coherent objective
- use `.github/PULL_REQUEST_TEMPLATE.md` as the standard description template
- explain why the change exists
- list the main technical decisions
- describe any architecture impact
- state the validation performed
- mention documentation updates
- state the version bump decision and list the files updated when the version changes
- mention follow-up work if relevant

Pull requests should be considered incomplete if they change behavior without updating the relevant documentation or without documenting the version bump decision.

For agent-authored pull requests, the description should also make clear that:

- the branch was prepared through the documented agent-driven workflow
- validation was executed before the pull request was opened
- merge is still reserved for a human maintainer review

When using `gh pr create`, agents should build the pull request body from `.github/PULL_REQUEST_TEMPLATE.md`, fill the relevant sections, and keep the validation and documentation checklist visible for reviewer audit.

## Merge Strategy

The standard merge mode should be `Squash and merge`.

Reasons:

- keeps `main` history compact
- makes the release history easier to read
- reduces noisy branch-level commit history in the permanent timeline
- works well with short-lived branches and PR review discipline

`Rebase and merge` may be tolerated later for very disciplined contributor flows, but it should not be the default.

`Merge commit` should remain disabled for now.

## Commit Convention

OrchFlow must use Conventional Commits for human-authored and agent-authored commits.

Commit messages should follow:

- `<type>: <imperative summary>`
- `<type>(<scope>): <imperative summary>`
- `<type>!: <imperative summary>` for intentional breaking changes
- `<type>(<scope>)!: <imperative summary>` for scoped intentional breaking changes

Recommended commit types:

- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `ci`
- `chore`

Optional scope format:

- `feat(core): add project entity skeleton`
- `fix(api): validate missing token`
- `docs(devops): define release process`
- `ci(repo): add backend validation workflow`
- `feat(ai): add LiteLLM gateway health checks`
- `feat(adapter): add authorized project context manifest`

Rules:

- write commits in imperative form
- keep each commit coherent
- avoid vague messages such as `update`, `changes`, or `misc`
- use `!` only when a change intentionally introduces a breaking contract
- choose a scope that matches the primary area changed, such as `ai`, `api`, `cli`, `web`, `adapter`, `registry`, `lifecycle`, `runtime`, `docs`, `ci`, or `repo`
- use the same commit convention for roadmap milestones, fixes discovered during a milestone, and documentation-only governance changes
- align the commit type with the version decision documented in the pull request

Roadmap implementation commits should be easy to read as release history. For example, the AI assistance sequence should use messages such as:

- `feat(ai): add LiteLLM gateway health checks`
- `feat(ai): add authorized project context manifest`
- `feat(ai): add reviewable lifecycle script proposals`
- `feat(ai): persist approved lifecycle mappings`

## Versioning Model

OrchFlow must use Semantic Versioning.

The project is currently in the `0.x` phase, so versioning should be interpreted with extra discipline:

- patch increments, such as `0.3.1` to `0.3.2`, for fixes, small internal improvements, documentation refinements, test additions, and CI changes that do not redefine product scope
- minor increments, such as `0.2.x` to `0.3.0`, for meaningful increments in product capability, public workflow shape, or project maturity
- `1.0.0` only when the public baseline is stable enough that breaking behavior becomes exceptional instead of expected

### Version Bump Guidance

Use:

- patch version when correcting behavior, adding narrowly scoped functionality inside the current milestone line, improving quality, or updating documentation/governance without materially expanding product scope
- minor version when adding a meaningful capability family, changing the public workflow shape, crossing an important delivery milestone, or completing a major Roadmap phase
- major version only after the project reaches `1.0.0`

Every pull request must evaluate whether the project version should change. When a bump is required, update all relevant version-bearing files in the same change set, including package metadata, runtime version constants, lockfiles, tests that assert version output, README/status documentation, and any workflow or roadmap documents that name the current version. If no bump is required, the pull request should explicitly say so.

Each Roadmap step must include a version decision before the pull request is opened. The decision should be based on the actual behavior introduced, not only on the commit type. For example, adding the first `AI Agent Adapter` plus `LiteLLM` boundary is a feature commit and requires a version bump because it introduces new public API/CLI behavior and architectural capability. A later internal refactor of the same boundary may use `refactor(ai)` and may keep the version unchanged only if the pull request proves there is no behavior, contract, dependency, workflow, or documentation-policy change.

### Commit Type And Version Relationship

The commit type does not mechanically determine the version bump, but it should guide the decision:

- `feat`: usually requires a version bump; patch while inside the current `0.x` milestone line for narrow increments, minor for larger capability phases
- `fix`: usually requires a patch bump when user-visible behavior changes
- `docs`: may require a patch bump when it changes governance, workflow policy, architecture, or documented product scope; may avoid a bump for wording-only corrections
- `refactor`: may require a patch bump if it changes operational behavior, public contracts, or supported workflows
- `test`: usually does not require a bump unless tests formalize a new public contract or release rule
- `ci`: may require a patch bump when CI changes release, validation, or merge requirements
- `chore`: should explain why the change is not product-visible; dependency or tooling changes may still require a bump

### Release Tag Format

Git tags should use the format:

- `v0.1.2`
- `v0.1.3`
- `v0.3.0`

The GitHub release title should match the tag version.

## Release Discipline

Each release should include:

- a version tag
- release notes
- a concise change summary
- notable documentation updates when relevant
- a list of known limitations when relevant

Before creating a release, confirm:

- CI is green on `main`
- documentation is aligned
- the repository is in a stable state
- the version in project metadata matches the intended release

## Local Validation Before Pull Request

Before opening a pull request, contributors should run the local validation commands relevant to the change.

For the current backend baseline, the expected validation direction is:

- `uv sync --dev`
- `uv run ruff check .`
- `uv run mypy src`
- `uv run alembic upgrade head`
- `uv run pytest`

The selected frontend package manager for `v0.3.2` is `pnpm`.

The expected frontend validation direction is:

- `corepack enable`
- `pnpm install`
- `pnpm lint`
- `pnpm test`
- `pnpm build`

## Documentation Gate

Changes should update documentation whenever they alter:

- architecture or policy
- workflow expectations
- setup or operational guidance
- module behavior
- implementation status

Before making changes, AI agents must read the applicable root-level documentation under `docs/`. They must not consult `docs/context/` unless the requesting user explicitly authorizes the specific feature context and the file is within the scope of the task.

At minimum, contributors should evaluate whether the change requires updates to:

- `docs/STATUS.md`
- `docs/INDEX.md`
- the relevant file in `docs/context/` for human contributors, or for AI agents only after explicit user authorization
- `docs/USER-GUIDE.md`
- this document
- project version references and metadata according to the versioning model

## Current CI Baseline

The repository validation workflow should run the current backend and frontend gates on pull requests and direct updates to `main`.

Backend gates:

- checkout
- Python setup
- `uv` installation
- dependency sync
- `ruff`
- `mypy`
- Alembic migration validation
- `pytest`
- OpenAPI contract coverage through the backend test suite

Frontend gates:

- checkout
- Node.js setup
- `pnpm` installation
- frontend dependency install
- frontend lint
- frontend tests
- frontend build verification

## CI Direction

CI should continue evolving in stages.

### Stage 1

The repository now has the backend and frontend quality baseline needed for `v0.3.2`.

### Stage 2

As product workflows grow:

- stricter unit, integration, and contract test separation when the suite becomes large enough to justify it
- more focused API contract assertions for newly exposed operator routes
- critical web-flow tests for new workflows before they become release expectations
- migration downgrade or drift checks if the migration model starts requiring them

### Stage 3

Release automation:

- version tag validation
- changelog or release note generation support
- release asset preparation if needed

## CD And DevOps Future Direction

Full CD should not be implemented before the product has stable build outputs worth distributing.

The recommended evolution is:

1. repository governance
2. CI quality gates
3. release discipline
4. packaging and artifact generation
5. delivery automation for stable product outputs

This sequencing keeps DevOps aligned with the project's local-first scope and avoids premature remote deployment complexity.

## GitHub Repository Configuration Standard

The remote repository should be configured to support this flow.

Required settings:

- protect `main`
- require pull requests before merge
- require at least one approval
- require status checks before merge
- require branches to be up to date before merge when CI is enabled
- disable direct pushes to `main`
- enable branch deletion after merge
- allow squash merge
- disable merge commits

### Review Model Notes

GitHub does not allow a pull request author to satisfy the required approval with their own review.

Because of that, repositories using agent-driven pull requests should treat the reviewer as a distinct human maintainer account from the PR author identity.

For a solo-maintainer repository, the recommended practical setup is:

- keep the primary maintainer account as the admin reviewer and merger
- create one dedicated GitHub identity for agent-authored pull requests
- grant that identity only the minimum repository access needed to create branches and pull requests
- authenticate local agent tooling with that dedicated identity instead of the maintainer identity

## Repository Identity Guidance

The preferred identity model for agent-driven work is:

- one dedicated GitHub user for repository automation and AI-authored pull requests
- repository-local Git `user.name` and `user.email` configuration matching that identity
- repository-scoped authentication for `git` and `gh`
- no reliance on the machine-global Git identity for agent-authored work

Recommended setup sequence:

1. create a dedicated GitHub account for agent-authored work
2. invite that account to the repository with write access
3. generate repository-scoped credentials for that identity
4. authenticate `git` and `gh` locally with that identity
5. set repository-local `git config user.name` and `git config user.email`
6. keep the maintainer account as the reviewer and merger on protected branches

Recommended supporting artifacts:

- pull request template
- issue templates
- labels for type, area, and priority
- code owners later, when the team structure justifies it

## Initial Label Model

Recommended labels:

- `type:feature`
- `type:bug`
- `type:docs`
- `type:refactor`
- `type:test`
- `type:ci`
- `type:chore`
- `area:core`
- `area:api`
- `area:cli`
- `area:web`
- `area:docs`
- `area:devops`
- `priority:high`
- `priority:medium`
- `priority:low`

## Operating Notes For Agents And Contributors

- do not bypass pull request review on protected branches
- do not treat documentation as optional
- do not bundle unrelated work into a single branch
- do not introduce release automation before basic CI is stable
- do not treat a green CI run as a substitute for design review
- do not let an agent use the maintainer's Git identity for authorship when a dedicated repository identity is expected

## Current Adoption State

As of `2026-08-24`, this workflow is documented and already supports both maintainer-authored and agent-authored pull requests for upcoming work.

The repository should continue evolving with:

- release automation
- deeper CI quality gates as implementation scope grows
- any future team-scaling rules that become necessary beyond the current maintainer plus agent model
