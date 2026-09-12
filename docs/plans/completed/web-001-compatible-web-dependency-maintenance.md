---
id: web-001
status: completed
type: chore
requires_pull_request: true
expected_version_impact: none
authorized_capabilities:
  - capabilities/web-operator-workspace/README.md
decision_records: []
validation:
  - frontend-lint
  - frontend-test
  - frontend-build
documentation_updates:
  - docs/STATUS.md
---

# Compatible Web Dependency Maintenance

## Objective

Update low-risk web dependencies within their current compatible major lines.

## Context

The web workspace needed a current, supported maintenance baseline before structural UI work starts. The requesting user explicitly approved activation and implementation on 2026-09-12.

## Decisions

Updated `lucide-react`, `@testing-library/react`, `@testing-library/jest-dom`, `@types/react`, `@types/react-dom`, `typescript-eslint`, and `eslint-plugin-react-refresh` to their selected compatible maintenance releases. `jest-dom` is pinned to `6.9.1`, the recommended 6.x line, instead of retaining the flagged `6.10.0` release. React/React DOM and all major toolchain migrations remain separate plans.

## Scope

Updated only the selected compatible dependency declarations and `pnpm-lock.yaml` entries.

## Out Of Scope

React runtime, Vite, TypeScript, Vitest, ESLint major migrations, and UI behavior changes.

## Acceptance Criteria

The selected versions install reproducibly and current lint, test, and build commands pass without workflow changes.

## Validation

Passed `corepack pnpm install`, `corepack pnpm lint`, `corepack pnpm test` (13 files and 44 tests), and `corepack pnpm build`.

## Documentation Updates

Updated the Roadmap and status dashboard to record completion and identify `web-002` as the next web plan.

## Outcome

Completed on 2026-09-12. Version decision: no bump for `web-001`; this is a compatible dependency-only maintenance change with no user-visible behavior, supported workflow, or public-contract change. Delivery commit: `f6e1a55d4d1ca75441ab7f2e487353d034ce30e6`. Pull request: [#56](https://github.com/0tter-Dev/OrchFlow/pull/56).
