# Configuration And Environment

## Purpose

This module defines how OrchFlow should manage runtime configuration.

## Objective

Provide a clear, versioned, environment-based configuration contract for local development and execution without mixing configuration concerns into domain rules.

## Current Status

`in_progress`

## Implemented Baseline

- validated settings loading, path normalization, runtime directory creation, and disabled-by-default LiteLLM settings are implemented
- `src/orchflow/infrastructure/config/contract.py` is the single versioned inventory of every supported backend, launcher, and web environment variable; it also owns diagnostic redaction for sensitive values
- `.env.example` and `interface/web/.env.example` define the current local configuration examples
- `orchflow-setup.bat` can create local `.env` files from those committed examples when the target files do not already exist as part of its setup/check flow
- `orchflow-control.bat` provides day-to-day API plus web status, start, stop, and restart after setup, while `orchflow-dev.bat` remains a combined entrypoint for both setup and control paths
- PID files, process metadata, generated command files, and startup logs for local OrchFlow API/web control are written under the configured `ORCHFLOW_RUNTIME_DIR`
- local OrchFlow API and web control reads `ORCHFLOW_API_HOST`, `ORCHFLOW_API_PORT`, `ORCHFLOW_WEB_HOST`, `ORCHFLOW_WEB_PORT`, and `ORCHFLOW_WEB_URL` from `.env` with process environment overrides
- the launchers preserve existing local `.env` files and report missing required local tools instead of installing global software automatically

## Direction

OrchFlow should adopt:

- environment variables as the primary runtime configuration source
- a versioned `.env.example` file as the public local configuration contract
- validated configuration loading near the application or infrastructure boundary
- separation between non-secret defaults and local secret values

## Configuration Contract Inventory

The committed `.env.example` files are examples, while the inventory below is the
authoritative configuration contract. `required` describes a value that must be
valid for its consumer; it does not make local secret editing available through
OrchFlow. `derived` values may be supplied as overrides but have a documented
fallback. There are no deprecated variables in `v0.3.41`.

| Variable | Owner / classification | Default | Format | Consumer | Sensitive |
| --- | --- | --- | --- | --- | --- |
| `ORCHFLOW_ENV` | backend / optional | `development` | string | settings | no |
| `ORCHFLOW_API_HOST` | backend / optional | `localhost` | hostname | settings | no |
| `ORCHFLOW_API_PORT` | backend / optional | `8000` | integer, 1–65535 | settings | no |
| `ORCHFLOW_DATABASE_URL` | backend / optional | `sqlite:///./data/orchflow.db` | SQLAlchemy URL | settings, persistence | no |
| `ORCHFLOW_JWT_SECRET` | backend / required | local placeholder | non-empty secret | authentication | yes |
| `ORCHFLOW_JWT_ALGORITHM` | backend / optional | `HS256` | JWT algorithm | authentication | no |
| `ORCHFLOW_JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | backend / optional | `60` | positive integer minutes | authentication | no |
| `ORCHFLOW_AI_ENABLED` | backend / optional | `false` | boolean | AI adapter | no |
| `ORCHFLOW_LITELLM_MODE` | backend / optional | `sdk` | string | LiteLLM gateway | no |
| `ORCHFLOW_LITELLM_BASE_URL` | backend / optional | `http://localhost:4000` | HTTP URL | LiteLLM gateway | no |
| `ORCHFLOW_LITELLM_API_KEY` | backend / optional | empty | secret | LiteLLM gateway | yes |
| `ORCHFLOW_LITELLM_DEFAULT_MODEL` | backend / optional | `ollama/llama2` | provider/model | AI adapter | no |
| `ORCHFLOW_LITELLM_TIMEOUT_SECONDS` | backend / optional | `60` | positive integer seconds | LiteLLM gateway | no |
| `ORCHFLOW_LOCAL_AI_PROVIDER_URL` | backend / optional | `http://localhost:11434` | HTTP URL | AI adapter | no |
| `ORCHFLOW_RUNTIME_DIR` | backend / optional | `./runtime` | local path | settings, launchers | no |
| `ORCHFLOW_DATA_DIR` | backend / optional | `./data` | local path | settings | no |
| `ORCHFLOW_LOG_LEVEL` | backend / optional | `INFO` | logging level | settings | no |
| `ORCHFLOW_WEB_HOST` | launcher / optional | `localhost` | hostname | Windows launchers | no |
| `ORCHFLOW_WEB_PORT` | launcher / optional | `5174` | integer, 1–65535 | Windows launchers | no |
| `ORCHFLOW_WEB_URL` | launcher / derived | `http://localhost:5174` | HTTP URL | Windows launchers | no |
| `VITE_API_BASE_URL` | web / optional | `/orchflow-api` | URL path or URL | web API client | no |

The backend loads `ORCHFLOW_*` values from process environment first and then
the root `.env`; unknown entries are ignored. The web build reads only
`VITE_*` values from `interface/web/.env`. Windows launchers read their local
endpoint and runtime values with process-environment overrides before `.env`.

Typed backend values are validated at settings construction, so invalid integer
settings fail at the application boundary with Pydantic validation details.
Sensitive values are never included in the existing CLI/API configuration
summary, and any future configuration diagnostic must use the contract's
redaction helper rather than expose a raw secret.

## Likely Configuration Areas

- application environment
- API host and port
- local web host, port, and URL
- web API base URL
- database file path
- JWT secret and token settings
- logging mode
- AI assistance enablement
- LiteLLM gateway mode, base URL, API key reference, model name, timeout, and local provider settings
- runtime artifact directories

## Key Rules

- `.env.example` should be committed
- real `.env` files should stay local and unversioned
- configuration loading should be explicit and testable
- missing critical configuration should fail clearly
- AI assistance must default to disabled until the LiteLLM gateway configuration is explicitly provided
- LiteLLM credentials and provider secrets must stay in local environment configuration, not source files
- API and CLI should expose the same configuration-facing capabilities when those capabilities are intentionally surfaced to operators

## Main Relationships

- supports `Access Control`
- supports `Persistence And Audit`
- supports `AI Assistance Adapter`
- supports `External Surfaces`
- supports `Interface Layer`
