# Configuration And Environment

## Purpose

This module defines how OrchFlow should manage runtime configuration.

## Objective

Provide a clear, versioned, environment-based configuration contract for local development and execution without mixing configuration concerns into domain rules.

## Current Status

`in_progress`

## Implemented Baseline

- validated settings loading, path normalization, runtime directory creation, and disabled-by-default LiteLLM settings are implemented
- `.env.example` and `interface/web/.env.example` define the current local configuration examples
- `orchflow-dev.bat` can create local `.env` files from those committed examples when the target files do not already exist
- the launcher preserves existing local `.env` files and reports missing required local tools instead of installing global software automatically

## Direction

OrchFlow should adopt:

- environment variables as the primary runtime configuration source
- a versioned `.env.example` file as the public local configuration contract
- validated configuration loading near the application or infrastructure boundary
- separation between non-secret defaults and local secret values

## Likely Configuration Areas

- application environment
- API host and port
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
