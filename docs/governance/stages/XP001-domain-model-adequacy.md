# XP001 — Domain model adequacy

Status: executed_partial_review_pending. Phase P01; gate G01; RQ1. Human review: pending.

Original source label: E001, **not an allocated experiment identity**. Permanent experiment: E003.

Prerequisite planning stages: research-definition review and live E003 scope authorization. E003's blocked review is the present project barrier; no successor execution is authorized.

## Implementation sequence

1. Recover repository/experiment context and obtain explicit prerequisite/scope authorization.
2. Preregister hypothesis, variables, controls, independent baseline, metrics and reviewed thresholds under an allocated permanent experiment ID.
3. Represent diverse failure states using one domain model; audit fields, identity, times, topology, labels and reconstruction.
4. Build fixtures and real/controlled integration tests covering stage-specific normal, boundary and failure cases.
5. Execute only the frozen protocol; retain dataset/code/configuration/environment provenance and unsuccessful attempts.
6. Compare against the declared reference; analyze uncertainty, coverage and failure categories.
7. Write evidence-backed decision and await human review; do not advance automatically.

## Controlled comparison and measures

Baseline/reference: Source rows/schema as oracle; cross-scenario fixtures.

Metrics: source fidelity; special-case fields; reconstruction completeness. Numeric thresholds/statistical acceptance: **not specified or approved**; preregister before execution.

Controls:

- Same versioned datasets/incidents and declared workload
- Independent branch inputs; no evaluation-label leakage
- Frozen selection/splits, tuning budget, configuration/seeds and hardware
- Preserve failures and non-overwriting source/result snapshots

## Required evidence and stop conditions

Artifacts: README.md, hypothesis.md, protocol.md, configuration.yaml, run.md, results/, figures/, logs/, decision.md, dataset/run/source manifests and hashes. Declare canonical/model/rule/preprocessing versions and distinguish actual runtime from static checks. Preserve source/labels separately. No existing-record edits without new authority.

STOP for missing approval, schema/semantic ambiguity, coverage gaps, leakage, invalid baseline, control changes, missing provenance or unmet acceptance. Distinguish model/engineering/source/coverage/environment failures. Propose PROCEED/REVISE/REPEAT/BRANCH/ABANDON; await an actual reviewer and scope authorization.

## Existing E003 evidence

Read `experiments/E003_domain_model_adequacy/decision.md`, `docs/E003-implementation-report.md`, and R001 result/run manifests. Required revisions remain unimplemented and unapproved; preserve executed v1. This card neither passes E003 nor authorizes a rerun.

## Original program intent (historical planning context)

The excerpt below retains the source's proposal, not an approved protocol or allocation. Source metrics/examples do not override the controls/approval requirement above.

### Hypothesis

> Our formal representation can encode the distributed-system states required by the planned reasoning experiments without introducing ad-hoc fields for each experiment.

### Test

Create representative incidents:

* dependency failure
* CPU saturation
* memory pressure
* network degradation
* database overload
* retry storm
* multiple simultaneous faults

Represent all of them using the same schema.

### Measure

```text
schema completeness
number of special-case fields
serialization/reconstruction fidelity
ability to reconstruct state
```

### Gate

If we need experiment-specific hacks:

**STOP → revise ontology.**

---

