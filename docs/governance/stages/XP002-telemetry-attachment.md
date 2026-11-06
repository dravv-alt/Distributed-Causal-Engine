# XP002 — Telemetry attachment

Status: planned_not_authorized. Phase P03; gate G03; RQ1. Human review: pending.

Original source label: E002, **not an allocated experiment identity**. Permanent experiment: UNALLOCATED.

Prerequisite planning stages: XP001. E003's blocked review is the present project barrier; no successor execution is authorized.

## Implementation sequence

1. Recover repository/experiment context and obtain explicit prerequisite/scope authorization.
2. Preregister hypothesis, variables, controls, independent baseline, metrics and reviewed thresholds under an allocated permanent experiment ID.
3. Attach a minimal instrumented service through SDK/Collector/OTLP-HTTP; validate retries, malformed payloads and durable acknowledgment.
4. Build fixtures and real/controlled integration tests covering stage-specific normal, boundary and failure cases.
5. Execute only the frozen protocol; retain dataset/code/configuration/environment provenance and unsuccessful attempts.
6. Compare against the declared reference; analyze uncertainty, coverage and failure categories.
7. Write evidence-backed decision and await human review; do not advance automatically.

## Controlled comparison and measures

Baseline/reference: Known emitted payloads versus received durable records.

Metrics: malformed/retry rates; acknowledgment durability; identity/unit fidelity. Numeric thresholds/statistical acceptance: **not specified or approved**; preregister before execution.

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

This is one of the five explicit initial spikes from the implementation plan:

> real OTLP ingestion. 

Test:

```text
Service
 ↓
OTel SDK
 ↓
Collector
 ↓
OTLP/HTTP
 ↓
DCE receiver
 ↓
durable storage
```

Verify:

* malformed payload handling
* retries
* acknowledgment semantics
* metric identity
* units
* timestamps
* resource identity
* trace ingestion

### Gate

No downstream experiment begins until ingestion is trustworthy.

---

