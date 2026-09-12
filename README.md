# OrchFlow

OrchFlow is a local-first project lifecycle orchestrator. It registers, controls, and inspects local software projects through explicit, reviewable Windows `.bat` lifecycle scripts.

## Quick Start

On Windows, run the repository entrypoint:

```bat
orchflow.bat
```

It guides local checks, setup, API and web startup, and routine process control. For contributor setup and validation, see the [development guide](./docs/DEVELOPMENT-GUIDE.md).

## Current Scope

- Local project registration, lifecycle control, runtime inspection, ownership, audit history, and operator preferences.
- Mirrored CLI, API, and web operator workflows.
- Optional LiteLLM-backed assistance that produces reviewable proposals; it never replaces the `.bat` lifecycle contract or human approval.

Out of scope in `v0.3.33`: container orchestration, multi-host control, automatic model downloads, and autonomous lifecycle control.

## Documentation

Start with [Start Here](./docs/START-HERE.md). It provides focused routes for operators, contributors, and AI agents.

- [Architecture](./docs/PROJECT-ARCHITECTURE.md)
- [Current status](./docs/STATUS.md)
- [Roadmap](./docs/ROADMAP.md)
- [Documentation guide](./docs/DOCUMENTATION-GUIDE.md)
- [Agent rules](./AGENTS.md)

## Selected Stack

Python, `uv`, Typer, FastAPI, SQLite, SQLAlchemy, Alembic, JWT, React, TypeScript, Vite, `pnpm`, and LiteLLM behind the OrchFlow AI assistance adapter.
