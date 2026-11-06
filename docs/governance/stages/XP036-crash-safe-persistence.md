# XP036 — Crash-safe persistence

Status: planned_not_authorized. Phase P15; gate G15; RQ8. Human review: pending.

Original source label: E036, **not an allocated experiment identity**. Permanent experiment: UNALLOCATED.

Prerequisite planning stages: XP035. E003's blocked review is the present project barrier; no successor execution is authorized.

## Implementation sequence

1. Recover repository/experiment context and obtain explicit prerequisite/scope authorization.
2. Preregister hypothesis, variables, controls, independent baseline, metrics and reviewed thresholds under an allocated permanent experiment ID.
3. Build minimum persistence/API/worker instrument then inject crashes before/after commits/notifications/leases; verify safe recovery.
4. Build fixtures and real/controlled integration tests covering stage-specific normal, boundary and failure cases.
5. Execute only the frozen protocol; retain dataset/code/configuration/environment provenance and unsuccessful attempts.
6. Compare against the declared reference; analyze uncertainty, coverage and failure categories.
7. Write evidence-backed decision and await human review; do not advance automatically.

## Controlled comparison and measures

Baseline/reference: Defined commit/notification/lease crash points; reference state.

Metrics: corruption/duplicate decisions; replay/ownership recovery. Numeric thresholds/statistical acceptance: **not specified or approved**; preregister before execution.

Controls:

- Same versioned datasets/incidents and declared workload
- Independent branch inputs; no evaluation-label leakage
- Frozen selection/splits, tuning budget, configuration/seeds and hardware
- Preserve failures and non-overwriting source/result snapshots

## Required evidence and stop conditions

Artifacts: README.md, hypothesis.md, protocol.md, configuration.yaml, run.md, results/, figures/, logs/, decision.md, dataset/run/source manifests and hashes. Declare canonical/model/rule/preprocessing versions and distinguish actual runtime from static checks. Preserve source/labels separately. No existing-record edits without new authority.

STOP for missing approval, schema/semantic ambiguity, coverage gaps, leakage, invalid baseline, control changes, missing provenance or unmet acceptance. Distinguish model/engineering/source/coverage/environment failures. Propose PROCEED/REVISE/REPEAT/BRANCH/ABANDON; await an actual reviewer and scope authorization.

## Original program intent (historical planning context)

The excerpt below retains the source's proposal, not an approved protocol or allocation. Source metrics/examples do not override the controls/approval requirement above.

The implementation plan explicitly calls for:

> crash-safe scope ownership and incident persistence. 

Test crashes:

```text
before DB commit
after DB commit
before notification
after notification
during lease
after lease expiry
```

Verify:

```text
no corrupted state
no duplicate decision
safe replay
correct ownership
```

---

