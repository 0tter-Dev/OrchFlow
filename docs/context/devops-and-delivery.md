# DevOps And Delivery

## Purpose

This module defines how OrchFlow itself should be versioned, validated, and delivered.

## Objective

Establish disciplined engineering workflows early so the codebase can evolve safely.

## Current Status

`in_progress`

## Focus Areas

- Git workflow
- GitHub collaboration
- `uv`-managed Python environments and dependencies
- versioned environment configuration examples
- multi-client repository structure for interface implementations
- pull request discipline
- automated checks
- semantic versioning
- release hygiene
- pull-request version bump discipline

## Current Documentation Baseline

The repository workflow baseline is documented in `docs/GIT-GITHUB-FLOW.md`.

This baseline defines:

- branch and pull request strategy
- merge policy
- human-driven and agent-driven contribution modes
- versioning and release discipline
- required version bump decision for each pull request
- staged CI direction
- future CD and DevOps sequencing
- expected GitHub repository settings

The repository now also includes:

- a pull request template
- issue templates for bugs, features, and focused tasks
- a GitHub Actions workflow that validates backend quality, Alembic migrations, backend tests, frontend lint, frontend tests, and frontend build
- hardened Alembic migration validation that checks the revision graph and schema drift against SQLAlchemy metadata
- backend OpenAPI contract coverage for authenticated operator routes and key response fields
- focused AI API contract coverage for authentication, validation, safe gateway responses, proposal workflow response shapes, and application confirmations
- version consistency contract coverage for synchronized package metadata, runtime version exposure, lockfiles, smoke tests, and current-version documentation references
- frontend critical-flow coverage for registering and selecting managed projects from the web operator surface

## Key Rules

- changes should be reviewable and traceable
- documentation, tests, and implementation should evolve together
- every pull request should evaluate and document the semantic version impact
- version-bearing files should be updated in the same pull request when the change advances the system version
- CI quality gates should be added early, even before full CD automation exists
- migration validation and API contract checks should remain part of the backend validation baseline once persistence and HTTP routes exist
- frontend lint, tests, and build should remain part of the validation baseline once web operator flows exist
- GitHub configuration should enforce the documented review flow instead of relying on convention alone
- agent-authored pull requests are acceptable when they remain reviewable, traceable, and constrained by a human merge authority

## Main Relationships

- governed by `Development Guide`
- supports the long-term maintainability of every other module
