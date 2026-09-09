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
