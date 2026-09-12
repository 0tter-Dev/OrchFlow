# Plans

Plans are focused work records. `backlog` holds approved future candidates, `active` holds the one or more explicitly approved work items being executed, and `completed` retains delivery outcomes.

## Plan Template

```yaml
---
id: area-001
status: backlog
type: docs
requires_pull_request: true
expected_version_impact: patch
authorized_capabilities: []
decision_records: []
validation: []
documentation_updates: []
---
```

Every plan body must contain `Objective`, `Context`, `Decisions`, `Scope`, `Out Of Scope`, `Acceptance Criteria`, `Validation`, `Documentation Updates`, and `Outcome`. An active plan must also record explicit user approval.

## Delivery Semantics

`requires_pull_request` is a required execution contract, not a reporting hint. An active plan whose body records explicit user approval and whose metadata sets `requires_pull_request: true` authorizes its agent to create the scoped branch from synchronized `main`, validate, commit, push, and open the pull request. It remains active until the pull request is open. `false` prohibits an agent-created pull request unless the user separately requests one.

Plan approval is intentionally narrow: it authorizes only the plan scope and the exact `authorized_capabilities` paths. It does not authorize additional capability reading, product-scope changes, public API changes, architectural decisions, strategic dependencies, or other actions that independently require approval.
