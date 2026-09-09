# Installer And Releases

## Purpose

This document captures the current planning direction for future OrchFlow installer and release packaging work.

It is intentionally descriptive. It does not introduce a current release artifact, installer implementation, desktop shell decision, or automated packaging workflow.

## Current Baseline

OrchFlow currently supports Windows-first local development through one repository-root launcher plus auxiliary launchers:

- `orchflow.bat` as the single root entrypoint for checks plus startup, browser opening, setup menu access, and control menu access
- `tools/windows/orchflow-setup.bat` for first-run setup, prerequisite checks, dependency installation, migrations, bootstrap validation, and API plus web startup
- `tools/windows/orchflow-control.bat` for routine status, start, stop, and restart of the local API plus web client through PID files and process metadata
- `tools/windows/orchflow-dev.bat` as the combined contributor entrypoint

These scripts remain the concrete operational base for the current project stage. Future installer work should reuse and wrap these explicit flows rather than replacing them with hidden lifecycle behavior.

## First Recommended Direction

The first recommended distribution direction is a lightweight Windows bootstrap `.exe`.

That bootstrap should:

- help a user start from a downloaded or cloned OrchFlow repository
- verify required local prerequisites instead of silently installing global software
- reuse `orchflow.bat` as the documented user-facing startup path
- reuse `tools/windows/orchflow-setup.bat` for setup/check behavior
- reuse `tools/windows/orchflow-control.bat` for day-to-day API and web process control
- preserve local `.env` files and user-owned project files
- report missing tools and failed setup steps clearly
- avoid taking over project lifecycle actions beyond the documented OrchFlow launchers

The bootstrap should act as a user-friendly entrypoint over the documented local-first workflow, not as a separate orchestration layer.

## Windows Bootstrap Executable Plan

The first bootstrap executable should be a thin Windows helper around the repository launchers. Its job is to make first startup easier for users who are not comfortable choosing scripts manually, while keeping the implementation reviewable and subordinate to the existing `.bat` flow.

### Responsibilities

The bootstrap executable should:

- locate the OrchFlow repository root from its own directory or from a user-selected folder
- verify that `orchflow.bat` exists before attempting startup
- verify required local prerequisites: `uv`, Node.js, and Corepack
- report missing prerequisites with short, actionable messages
- call `orchflow.bat` or its documented delegated flows instead of reimplementing setup logic
- run the equivalent of checks plus startup through the existing launcher path
- open the local web interface after startup succeeds
- preserve existing `.env`, `interface/web/.env`, `data/`, `runtime/`, and user-owned project files
- return a non-zero exit code when prerequisite checks, setup, or startup fail

### Delegation Model

The bootstrap should treat `orchflow.bat` as the user-facing startup contract.

The executable may call:

- `orchflow.bat` for the standard interactive path
- `tools/windows/orchflow-setup.bat check` for non-interactive setup/check validation
- `tools/windows/orchflow-control.bat start` for startup after successful checks
- `tools/windows/orchflow-control.bat status` for optional post-start diagnostics

The executable should not duplicate dependency installation, migration, process control, PID tracking, or environment-file creation logic. Those responsibilities remain inside the existing launchers and PowerShell process-control script.

### User Experience

The first prototype can be intentionally simple. It should provide:

- a visible startup status sequence for prerequisite checks, setup/check execution, API/web startup, and browser opening
- clear failure messages that include the failed step and the launcher command that failed
- a final success message with the local web URL
- a way to leave the terminal/window open long enough for users to read failures

The bootstrap should open `ORCHFLOW_WEB_URL` when configured. If that value is absent, it should use `ORCHFLOW_WEB_HOST` and `ORCHFLOW_WEB_PORT`, falling back to `http://localhost:5174`, matching `orchflow.bat`.

### Explicit Non-Goals

The first bootstrap executable must not:

- install global software automatically
- download Python, Node.js, AI models, or provider runtimes
- replace `orchflow.bat` as the documented startup contract
- start, stop, or restart registered user projects directly
- bypass `tools/windows/orchflow-control.bat` for API/web process ownership
- implement container, cloud, remote, or multi-host orchestration
- introduce Tauri, Electron, or another desktop shell decision by implication
- require administrator privileges for normal startup

### Prototype Implementation Shape

The next implementation PR should choose the smallest practical Windows-native path that can be built and reviewed in this repository. A small source file plus a documented build command is preferable to a large packaging framework.

The prototype should include:

- source for the bootstrap executable under a reviewable repository path
- a documented local build command
- a generated executable only if the repository release-artifact policy explicitly allows committing that artifact
- tests or contract checks for the documented commands and expected launcher paths where practical
- README and user-guide updates explaining when to use the executable versus `orchflow.bat`

### Validation For The Prototype PR

The prototype PR should validate:

- executable build succeeds on Windows
- missing-prerequisite reporting remains clear
- setup/check delegation reaches `tools/windows/orchflow-setup.bat check`
- startup delegation reaches `tools/windows/orchflow-control.bat start`
- browser URL resolution matches `orchflow.bat`
- existing local `.env` files are not overwritten
- backend validation remains green
- frontend validation remains green when web build or startup assumptions change

### Release Artifact Expectations

Until a later release workflow is approved, the bootstrap executable should be treated as a local build output or review artifact, not an automatically published release. If a PR produces a binary artifact, reviewers should verify how it was built and whether it belongs in Git, in a GitHub Actions artifact, or only in a future release.

## Candidate Release Shapes

Future releases may be discussed in these shapes:

| Shape | Contents | Intended Use | Current Decision |
| --- | --- | --- | --- |
| `CLI only` | Python package and CLI entrypoint | operators who prefer terminal-only local control | future option |
| `CLI + API` | backend package, API server, and CLI | local automation or custom clients | future option |
| `CLI + API + Web` | backend, CLI, and built web client | default local operator experience candidate | future option |
| `CLI + API + Desktop App` | backend, CLI, API, and a desktop shell | later desktop evaluation candidate | undecided |
| `All included` | backend, CLI, API, web, desktop shell, scripts, and helper assets | later complete local bundle candidate | undecided |

The current repository should continue stabilizing the `CLI + API + Web` local workflow before committing to desktop packaging or all-in-one installers.

## Archive-Based Releases

A full-project `.zip` release may be useful before a dedicated installer exists.

A `.zip` release could include:

- source tree or prepared release tree
- Windows launcher scripts
- web build output when the release shape includes the web client
- documentation needed for setup and operation
- generated release notes

A `.zip` release should still rely on explicit setup/control scripts and should not imply that OrchFlow installs or manages global prerequisites automatically.

## Desktop Shell Evaluation

Desktop shell choices remain undecided.

Future evaluation may compare options such as:

- no desktop shell, keeping browser-based web UI plus scripts
- Tauri
- Electron
- another Windows-focused wrapper

That evaluation should happen in a dedicated Roadmap step after the web and launcher flows are stable enough to justify packaging decisions. The evaluation should consider local-first behavior, installer size, update model, security boundaries, development maintenance cost, and how clearly the shell preserves the API-consuming interface boundary.

## Constraints

Future installer and release work should:

- preserve the Windows `.bat` launcher model as the operational base until a later approved architecture decision changes it
- avoid container, cloud, multi-host, or remote orchestration assumptions
- keep release artifacts reviewable before publication
- keep generated release notes as review artifacts unless a later workflow explicitly promotes them to published release notes
- avoid selecting Tauri, Electron, or another desktop shell by implication
- align future branded installer assets with `docs/BRAND-IDENTITY.md`
- document any new release workflow expectations in `docs/GIT-GITHUB-FLOW.md`

## Current Status

This document is planning guidance only. Current local development and validation flows remain defined by the existing launchers, GitHub Actions validation workflow, manual release validation workflow, and release discipline documented in `docs/GIT-GITHUB-FLOW.md`.
