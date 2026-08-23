# Access Control

## Purpose

This module defines authentication and authorization behavior for OrchFlow users.

## Objective

Ensure that project visibility and lifecycle actions are restricted according to user identity and granted permissions.

## Current Status

`planned`

## Roles

- `member`: standard user with permission-scoped access
- `admin`: full access to projects, users, and permissions

## Responsibilities

- user registration
- authentication
- session or token validation
- permission checks
- project access enforcement
- admin management operations

## Key Rules

- permissions must be enforced consistently across CLI, API, and interface channels
- access control decisions belong in the application core, not only in adapters
- admin capabilities must be explicit and auditable

## Main Relationships

- governs access to `Project Registry`
- constrains `Lifecycle Orchestration` actions
- affects what appears in `External Surfaces` and `Interface Layer`
