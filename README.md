# OrchFlow

OrchFlow is a local-first project lifecycle orchestrator focused on registering, controlling, and inspecting software projects through a standardized operational contract.

In `v0.3.22`, OrchFlow is designed around a concrete execution base: each managed project must expose a lifecycle control script, initially standardized as a Windows `.bat` file. OrchFlow compares those scripts against an ideal lifecycle function model so projects can be classified as completely configured, partially configured with warnings, or blocked when no lifecycle function is configured. Users can explicitly reload one project or multiple projects after local `.bat` changes so OrchFlow refreshes detection, preserves valid user decisions, and audits the before/after configuration health. Lifecycle execution now runs only configured actions; undefined or explicitly unconfigured actions return operator-facing feedback instead of falling back to assumed script labels. The API and CLI now expose non-AI project updates for metadata, lifecycle script paths, lifecycle mappings, and backend-owned user preferences while preserving validation and auditability. Runtime inspection now uses `APP_URL` reachability when `APP_PORT` is absent, reports unsupported states when no runtime hints exist, explains URL timeouts in operator-facing diagnostics, and supports authorized batch inspection so visible project lists can refresh runtime status efficiently. Admin audit history now supports filters by actor, action, project, and time window across API, CLI, and web. The web workspace now uses a compact daily operator layout with top API/session status, project navigation, command metrics, selected-project details, runtime diagnostics, preferences, admin tools, audit, and AI proposal review while honoring locale, project list/table display, and status refresh preferences. OrchFlow now exposes authenticated, audited AI assistance status, LiteLLM gateway health, model discovery, authorized context manifests, reviewable analysis proposals, proposal review decisions, and explicit application of approved proposals across backend contracts and the web operator surface. Proposal creation may send only manifest-approved context to LiteLLM; approval validates the candidate `.bat` and mappings before accepting the review; application requires separate file-write and mapping-persistence confirmations before writing the lifecycle `.bat`, persisting effective `ai_approved` mappings, and recording an application audit trail. AI API routes now have focused contract tests for authentication, validation, safe gateway responses, manifest/proposal/review/application response shapes, and explicit application confirmations. Version-bearing metadata, runtime constants, lockfiles, smoke tests, and current-version documentation references now have repository contract tests that enforce synchronization. Alembic migration validation now checks the revision graph and schema drift against SQLAlchemy metadata. Release validation now has a manual GitHub Actions workflow for tag checks and generated release-note artifacts. Roadmap planning now treats each numbered `docs/TO-DO.md` step as one pull-request-sized change by default. A Windows-first local development launcher is now available at `orchflow-dev.bat` to guide cloned repositories through prerequisite checks, local `.env` preparation, dependency installation, database migrations, bootstrap validation, and starting the API plus web development servers.

## Selected Stack

- Core runtime: Python
- Dependency and environment management: `uv`
- CLI: `Typer`
- API: `FastAPI`
- Persistence: `SQLite`
- ORM and migrations: `SQLAlchemy` and `Alembic`
- Authentication: JWT with password hashing through `bcrypt`
- Quality tooling: `pytest`, `ruff`, `mypy`
- Frontend package manager: `pnpm`
- Web interface: `React`, `TypeScript`, and `Vite`
- AI/model gateway: `LiteLLM`, isolated behind the OrchFlow AI assistance adapter

## Documentation

- [Project Architecture](./docs/PROJECT-ARCHITECTURE.md)
- [Documentation Index](./docs/INDEX.md)
- [Feature Status](./docs/STATUS.md)
- [Development Guide](./docs/DEVELOPMENT-GUIDE.md)
- [User Guide](./docs/USER-GUIDE.md)
- [To-Do](./docs/TO-DO.md)
- [Agent Rules](./AGENTS.md)

## Initial Scope

- Local-first project orchestration
- Project registration through `.bat` lifecycle scripts
- Ideal lifecycle function mapping for `status`, `start`, `stop`, and `restart`
- Explicit project reload to refresh lifecycle script detection after local changes
- Authenticated AI assistance status, LiteLLM gateway health, model discovery, authorized context manifests, reviewable analysis proposals, proposal review decisions, and approved proposal application through an OrchFlow-owned adapter boundary and web operator UI, with file writes and mapping persistence gated by explicit confirmation
- Lifecycle operations: status, start, stop, restart
- Basic runtime inspection: single and batch checks for ports, URLs, reachability, process hints, uptime, CPU, memory, and clear unsupported or timeout diagnostics
- User authentication and authorization with `admin` and `member`
- External access through `CLI`, `API`, and a compact web operator workspace with project editing
- Backend-owned user preferences for locale, project display mode, and status refresh interval

## Repository Foundation

- `pyproject.toml` defines the Python package metadata and the initial backend toolchain
- `.env.example` should define the documented local configuration contract
- `.gitignore` excludes Python, UI, database, and local runtime artifacts
- `.gitattributes` normalizes line endings while preserving Windows-oriented script compatibility
- `.editorconfig` defines shared editor behavior
- `LICENSE` currently uses `MIT`
- `interface/` should act as the physical boundary for API-consuming clients such as web, mobile, and desktop

## Local Setup

For Windows development, the recommended starting point is:

```bat
orchflow-dev.bat
```

The launcher provides menu-driven steps to check local prerequisites, create `.env` and `interface/web/.env` from the committed examples when they do not already exist, install backend and frontend dependencies, run migrations, validate bootstrap CLI commands, and start the API plus web client. It preserves existing local `.env` files and reports missing tools instead of installing global software automatically.

The manual backend setup remains:

```bash
uv sync --dev
```

This project uses `uv` as the source of truth for Python dependency resolution and local environment management.

For the web client, the selected JavaScript package manager is `pnpm`.

```bash
corepack enable
pnpm --version
cd interface/web
pnpm install
pnpm dev
```

The current backend validation flow is:

```bash
uv run ruff check .
uv run mypy src
uv run pytest
uv run alembic upgrade head
```

The current frontend validation flow is:

```bash
cd interface/web
pnpm lint
pnpm test
pnpm build
```

For local runtime configuration, copy `.env.example` into a local `.env` file and adjust the values for your machine.

The `interface/web` client now defaults to `VITE_API_BASE_URL=/orchflow-api` so local Vite development can proxy API traffic to the backend without changing backend contracts.

## Out Of Scope For v0.3.22

- Container orchestration
- Multi-host orchestration
- Automatic model downloads
- Distributed observability
- Complex infrastructure automation

## Status

The repository is currently in the `v0.3.22` implementation stage with the backend foundation, mirrored API and CLI operational surfaces, persisted user web preferences, runtime inspection refinement for `APP_URL`-only projects, authorized batch runtime inspection, compact web operator workspace, clearer unsupported/timeout diagnostics, filtered admin audit history across API, CLI, and web, CI and API contract hardening, focused AI API contract tests, version consistency contract tests, hardened Alembic revision graph and schema drift tests, manual release tag validation plus generated release-note artifacts, LiteLLM dependency baseline, explicit project reload, configured-action lifecycle execution gating, non-AI project update workflows for metadata, lifecycle script paths, and lifecycle mappings, web project editing, web lifecycle configuration indicators plus mapping controls, guided operational readiness, first-project and selected-project onboarding guidance, richer web error states, runtime diagnostic actions, roadmap governance for one-PR-sized planning steps, a Windows-first local development launcher, and authenticated AI assistance status, gateway health, model discovery, authorized context manifests, reviewable analysis proposals, proposal review decisions, and explicit approved proposal application implemented on top of those contracts.

The current web baseline includes authenticated session loading, a compact operator workspace shell, persisted user preferences, project listing with batch runtime status, project details, project editing, runtime inspection visibility, operational readiness guidance, richer API error notices, lifecycle controls, and AI proposal review/application wired directly through the API.
