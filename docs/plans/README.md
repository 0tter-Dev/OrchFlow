# Plans

Plans are focused work records with lifecycle `backlog → active → review → completed`; `cancelled` is the terminal alternative. `review` holds open delivery PRs and `completed` holds merged outcomes.

## Plan Template

```yaml
---
id: area-001
status: backlog
type: docs
requires_pull_request: true
expected_version_impact: patch
actual_version_impact: pending
priority: medium
sequence: 0
depends_on: []
authorized_capabilities: []
decision_records: []
validation: []
documentation_updates: []
---
```

Every plan body must contain `Objective`, `Context`, `Decisions`, `Scope`, `Out Of Scope`, `Acceptance Criteria`, `Validation`, `Documentation Updates`, and `Outcome`. An active plan must also record explicit user approval. `priority` expresses urgency, `sequence` identifies the Roadmap position, and `depends_on` names only hard prerequisite plan IDs. Review plans and plans completed under this lifecycle record PR URL, delivery commit, validation, and final `actual_version_impact`; a difference from expected impact is justified in `Outcome`.

## Delivery Semantics

`requires_pull_request` is a required execution contract, not a reporting hint. Every new plan is a delivery plan and must set it to `true`. Work that does not independently need a pull request is a phase, task, or acceptance criterion within its parent delivery plan and has no independent plan lifecycle. An active plan whose body records explicit user approval authorizes its agent to create the scoped branch from synchronized `main`, validate, commit, push, and open the pull request. It moves to `review` in that PR and to `completed` only after merge plus local `main` synchronization.

### Delivery Checklist

| Phase | Required plan and delivery actions |
| --- | --- |
| Before implementation | Reconcile every `active` and `review` plan with GitHub and local `main`; synchronize `main`; for every review plan whose delivery PR is merged, move it to `completed` and reconcile its Roadmap and status references before activating a later plan; confirm the first eligible Roadmap item and its completed dependencies; inspect the plan for every proposed new dependency and obtain one explicit user authorization covering the full declared dependency set before implementation begins; record explicit approval in the plan; create the branch from that baseline. |
| During implementation | Stay within the approved scope and `authorized_capabilities`; update affected implementation and owning documentation; run the plan's relevant validation; confirm the actual Conventional Commit and semantic-version decision against the diff. |
| When the delivery PR is open | Push the validated commit, open the PR, move the plan from `active` to `review` in that same PR, update `ROADMAP.md` and `STATUS.md`, and record the PR URL, delivery commit, validation result, and final `actual_version_impact` in the plan outcome. |
| After merge | Synchronize local `main`, move the plan from `review` to `completed`, and record the merged outcome, validation, expected and actual version decision, commit, and PR reference. Do not activate a later Roadmap item while an earlier plan remains unreconciled. |

## Ordering And Eligibility

`docs/ROADMAP.md` is the canonical ordered queue. Its `Sequence` defines the default order; `priority` is a triage signal (`high`, `medium`, or `low`) and must not silently reorder work. `depends_on` lists only hard prerequisite plan IDs. A backlog plan is eligible when every dependency is completed and there is no earlier Roadmap item that remains active, in review, blocked, or otherwise unreconciled. Only the first eligible plan may move to `active` by default. Parallel activation or a sequence change requires explicit user approval and a corresponding Roadmap update.

Plan approval is intentionally narrow: it authorizes only the plan scope and the exact `authorized_capabilities` paths. It does not authorize additional capability reading, product-scope changes, public API changes, architectural decisions, strategic dependencies, or other actions that independently require approval.
