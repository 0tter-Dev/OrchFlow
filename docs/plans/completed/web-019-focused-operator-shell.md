---
id: web-019
status: completed
type: feat
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: none
priority: medium
sequence: 18
depends_on:
  - web-018
authorized_capabilities:
  - capabilities/web-operator-workspace/README.md
  - capabilities/access-control/README.md
decision_records: []
validation:
  - frontend-lint
  - frontend-test
  - frontend-build
  - critical-browser-workflow-test
documentation_updates:
  - docs/capabilities/web-operator-workspace/README.md
  - docs/guides/user-guide.md
---

# Focused Operator Shell

## Objective

Evolve the desktop-first workspace into a calm, directed operator shell with focused navigation and account access, while retaining the current local-first controls and route-level authorization.

## Approval

The requesting user explicitly approved activation and implementation on 2026-09-21.

## Scope

- replace the persistent, attention-heavy navigation treatment with a discoverable menu control and collapsible navigation surface suitable for notebook and desktop use;
- redesign the top band around `menu | compact product mark and contextual title | user avatar`, keeping operational status available without competing with primary work;
- expose profile and session actions through an avatar-triggered account menu; use compact modal or popover interactions only for simple, non-sensitive information and configuration;
- make the central workspace the visual focus, reduce redundant branding, and preserve direct access to authorized routes;
- ensure the shell remains visually stable at medium and large desktop widths without claiming a full mobile-responsive redesign;
- keep styles component-owned or token-driven and avoid inline-style layout patches.

## Out Of Scope

Mobile-first redesign, a new visual brand, removal of authorized routes, authentication changes, or moving sensitive account flows into an unsafe modal.

## Acceptance Criteria

- users can discover and operate every authorized workspace route from the menu without a permanently dominant sidebar;
- the current user can reach profile and sign-out actions through the avatar menu with keyboard-accessible controls;
- top-band and primary-content hierarchy stay clear across the supported notebook and desktop widths;
- visual regression and browser checks cover menu, account-menu, keyboard, and selected-route behavior;
- the implementation uses reusable shell components and CSS tokens/classes rather than one-off inline styling.

## Outcome

Delivered through PR [#86](https://github.com/0tter-Dev/OrchFlow/pull/86), merged on 2026-09-22 in commit `a16635b`. The focused shell provides a keyboard-accessible navigation menu and avatar account menu while retaining route-level authorization. Frontend lint, test, build, and browser workflow checks passed. The expected patch version impact was not applied in this historical delivery; actual impact was `none`.
