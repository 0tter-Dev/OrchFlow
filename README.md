# OrchFlow

OrchFlow is a local-first project lifecycle orchestrator focused on registering, controlling, and inspecting software projects through a standardized operational contract.

In `v0.1.0`, OrchFlow is designed around a concrete execution base: each managed project must expose a lifecycle control script, initially standardized as a Windows `.bat` file. OrchFlow may optionally use an `AI Agent Adapter` to analyze a selected project folder and help the user generate that `.bat` file, but AI assistance is never the primary source of truth for lifecycle control.

## Documentation

- [Project Architecture](./docs/PROJECT-ARCHITECTURE.md)
- [Documentation Index](./docs/INDEX.md)
- [Feature Status](./docs/STATUS.md)
- [Development Guide](./docs/DEVELOPMENT-GUIDE.md)
- [User Guide](./docs/USER-GUIDE.md)
- [To-Do](./TO-DO.md)
- [Agent Rules](./AGENTS.md)

## Initial Scope

- Local-first project orchestration
- Project registration through `.bat` lifecycle scripts
- Optional project analysis through an `AI Agent Adapter`
- Lifecycle operations: status, start, stop, restart
- Basic runtime inspection: ports, processes, uptime, CPU, memory
- User authentication and authorization with `admin` and `member`
- External access through `CLI`, `API`, and a simple visual interface

## Out Of Scope For v0.1.0

- Container orchestration
- Multi-host orchestration
- Automatic model downloads
- Distributed observability
- Complex infrastructure automation

## Status

The repository is currently in the documentation-first foundation stage. The initial architectural documentation defines the product boundaries, domain concepts, feature map, and development rules before source code implementation begins.
