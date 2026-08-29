# OrchFlow

OrchFlow is a local-first project lifecycle orchestrator focused on registering, controlling, and inspecting software projects through a standardized operational contract.

In `v0.2.14`, OrchFlow is designed around a concrete execution base: each managed project must expose a lifecycle control script, initially standardized as a Windows `.bat` file. OrchFlow compares those scripts against an ideal lifecycle function model so projects can be classified as completely configured, partially configured with warnings, or blocked when no lifecycle function is configured. Users can explicitly reload one project or multiple projects after local `.bat` changes so OrchFlow refreshes detection, preserves valid user decisions, and audits the before/after configuration health. Lifecycle execution now runs only configured actions; undefined or explicitly unconfigured actions return operator-facing feedback instead of falling back to assumed script labels. OrchFlow may optionally use a LiteLLM-backed AI assistance adapter to analyze an explicitly authorized project context and help the user generate a reviewable `.bat` proposal, but AI assistance is never the primary source of truth for lifecycle control.

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
- Optional project analysis through a review-driven AI assistance adapter using LiteLLM as the planned model gateway
- Lifecycle operations: status, start, stop, restart
- Basic runtime inspection: ports, processes, uptime, CPU, memory
- User authentication and authorization with `admin` and `member`
- External access through `CLI`, `API`, and a simple visual interface

## Repository Foundation

- `pyproject.toml` defines the Python package metadata and the initial backend toolchain
- `.env.example` should define the documented local configuration contract
- `.gitignore` excludes Python, UI, database, and local runtime artifacts
- `.gitattributes` normalizes line endings while preserving Windows-oriented script compatibility
- `.editorconfig` defines shared editor behavior
- `LICENSE` currently uses `MIT`
- `interface/` should act as the physical boundary for API-consuming clients such as web, mobile, and desktop

## Local Setup

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

## Out Of Scope For v0.2.14

- Container orchestration
- Multi-host orchestration
- Automatic model downloads
- Distributed observability
- Complex infrastructure automation

## Status

The repository is currently in the `v0.2.14` implementation stage with the backend foundation, mirrored API and CLI operational surfaces, runtime inspection refinement, CI and API contract hardening, LiteLLM dependency baseline, explicit project reload, configured-action lifecycle execution gating, and the first practical `interface/web` operator flow now implemented on top of those contracts.

The current web baseline includes authenticated session loading, project listing, project details, runtime inspection visibility, and the first lifecycle controls wired directly through the API.
