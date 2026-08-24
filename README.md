# OrchFlow

OrchFlow is a local-first project lifecycle orchestrator focused on registering, controlling, and inspecting software projects through a standardized operational contract.

In `v0.1.2`, OrchFlow is designed around a concrete execution base: each managed project must expose a lifecycle control script, initially standardized as a Windows `.bat` file. OrchFlow may optionally use an `AI Agent Adapter` to analyze a selected project folder and help the user generate that `.bat` file, but AI assistance is never the primary source of truth for lifecycle control.

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
- Optional project analysis through an `AI Agent Adapter`
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

For local runtime configuration, copy `.env.example` into a local `.env` file and adjust the values for your machine.

## Out Of Scope For v0.1.2

- Container orchestration
- Multi-host orchestration
- Automatic model downloads
- Distributed observability
- Complex infrastructure automation

## Status

The repository is currently in the `v0.1.2` bootstrap implementation stage. The architectural documentation is established, the stack baseline is defined, the backend foundation is active, and the first web bootstrap now exists in `interface/web`.
