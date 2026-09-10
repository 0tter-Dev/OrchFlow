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
