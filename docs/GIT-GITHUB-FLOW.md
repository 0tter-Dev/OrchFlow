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

This project should not adopt a heavy Git Flow model in `v0.1.2`.

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

## Pull Request Rules

Every pull request should:

- target `main`
- solve one coherent objective
- explain why the change exists
- list the main technical decisions
- describe any architecture impact
- state the validation performed
- mention documentation updates
- mention follow-up work if relevant

Pull requests should be considered incomplete if they change behavior without updating the relevant documentation.

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

OrchFlow should use Conventional Commits.

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

Rules:

- write commits in imperative form
- keep each commit coherent
- avoid vague messages such as `update`, `changes`, or `misc`
- use `!` only when a change intentionally introduces a breaking contract

## Versioning Model

OrchFlow should use Semantic Versioning.

The project is currently in the `0.x` phase, so versioning should be interpreted with extra discipline:

- `0.1.z` for fixes, small internal improvements, documentation refinements, test additions, and CI changes that do not redefine product scope
- `0.x.0` for meaningful increments in product capability or project maturity
- `1.0.0` only when the public baseline is stable enough that breaking behavior becomes exceptional instead of expected

### Version Bump Guidance

Use:

- patch version when correcting behavior or improving quality without materially expanding scope
- minor version when adding meaningful capability or crossing an important delivery milestone
- major version only after the project reaches `1.0.0`

### Release Tag Format

Git tags should use the format:

- `v0.1.2`
- `v0.1.3`
- `v0.2.0`

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
- `uv run pytest`

When the frontend is introduced, this document should be extended with the corresponding validation commands for `interface/web`.

The selected frontend package manager for `v0.1.2` is `pnpm`.

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

At minimum, contributors should evaluate whether the change requires updates to:

- `docs/STATUS.md`
- `docs/INDEX.md`
- the relevant file in `docs/context/`
- `docs/USER-GUIDE.md`
- this document

## CI Direction

CI should be introduced in stages.

### Stage 1

Repository quality gates:

- checkout
- Python setup
- `uv` installation
- dependency sync
- `ruff`
- `mypy`
- `pytest`

### Stage 2

As backend code grows:

- stricter unit and integration test separation
- migration validation
- API contract validation

### Stage 3

When the web client exists:

- frontend install
- frontend lint
- frontend tests
- frontend build verification

### Stage 4

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

## Current Adoption State

As of `2026-08-23`, this workflow is documented and should be treated as the intended standard for upcoming work.

The repository still needs:

- remote GitHub configuration
- branch protection rules
- release automation

Those items should be implemented incrementally according to this document.
