# Access Control

## Purpose

This module defines authentication and authorization behavior for OrchFlow users.

## Objective

Ensure that project visibility and lifecycle actions are restricted according to user identity, role, and project ownership.

## Current Status

`implemented`

## Roles

- `member`: standard user with access to owned projects
- `admin`: full access to projects, users, roles, activation state, and ownership assignments

## Responsibilities

- user registration
- authentication
- session or token validation
- permission checks
- project access enforcement
- admin management operations

## Implemented Baseline

- first registered user becomes the bootstrap `admin`
- users can authenticate through JWT-backed login
- admins can list users
- admins can update user roles and activation state
- updates that would remove the last active admin are rejected
- admin user-management actions are audited
- admin-only audit history filtering is implemented for actor, action, project, and time-window troubleshooting
- project visibility and lifecycle access are enforced through the `admin` role or explicit project ownership

## Key Rules

- role and ownership access rules must be enforced consistently across CLI, API, and interface channels
- access control decisions belong in the application core, not only in adapters
- admin capabilities must be explicit and auditable
- at least one active admin user must remain available
- the first registered user may become the bootstrap `admin` so the local-first installation can be initialized without a pre-provisioned account
- API and CLI should expose the same authentication and authorization capabilities when those capabilities are intentionally available to operators
- a separate generic permission table is not part of the current implemented baseline

## Main Relationships

- governs access to `Project Registry`
- constrains `Lifecycle Orchestration` actions
- affects what appears in `External Surfaces` and `Interface Layer`
