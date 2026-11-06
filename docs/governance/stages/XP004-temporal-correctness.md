# XP004 — Temporal correctness

Status: planned_not_authorized. Phase P04; gate G04; RQ1. Human review: pending.

Original source label: E004, **not an allocated experiment identity**. Permanent experiment: UNALLOCATED.

Prerequisite planning stages: XP003. E003's blocked review is the present project barrier; no successor execution is authorized.

## Implementation sequence

1. Recover repository/experiment context and obtain explicit prerequisite/scope authorization.
2. Preregister hypothesis, variables, controls, independent baseline, metrics and reviewed thresholds under an allocated permanent experiment ID.
3. Implement alignment, masks and bounded late-event/reset policies; compare event-time windows under disorder before ML.
4. Build fixtures and real/controlled integration tests covering stage-specific normal, boundary and failure cases.
5. Execute only the frozen protocol; retain dataset/code/configuration/environment provenance and unsuccessful attempts.
6. Compare against the declared reference; analyze uncertainty, coverage and failure categories.
7. Write evidence-backed decision and await human review; do not advance automatically.

## Controlled comparison and measures

Baseline/reference: Same event set with permuted arrival order; offline oracle.

Metrics: online/offline equality; missing/reset/late handling. Numeric thresholds/statistical acceptance: **not specified or approved**; preregister before execution.

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

Create synthetic disorder:

```text
event 1 → arrives 100ms late
event 2 → arrives before event 1
event 3 → missing
event 4 → counter reset
```

Compare:

```text
online processing
vs
offline replay
```

### Desired result

Same logical event-time window should produce the same diagnosis regardless of arrival ordering.

### If it fails

We fix the temporal engine **before touching ML**.

---

