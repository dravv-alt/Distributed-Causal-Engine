# DCE — Real-World RCA Transition

## Executable Agent Prompt: E003 Remediation → RCAEval Integration Readiness

You are operating inside the **Distributed - NeuroSymbolicAI (DCE)** research repository.

Your task is to move the project from validated synthetic/reproduction experiments toward **real-world distributed-system Root Cause Analysis (RCA)** using the existing telemetry infrastructure and the RCAEval benchmark.

This is a **research experiment and infrastructure task**, not a request to immediately build an AI model.

Your primary responsibility is to produce a scientifically defensible transition from:

```text
E001/E002
validated experimental methodology
        ↓
E003
telemetry representation validation
        ↓
E003 remediation
        ↓
real telemetry representation
        ↓
RCAEval
benchmark + evaluation
        ↓
future symbolic/neural RCA
```

Do NOT skip the representation/validation stage in order to build an RCA model.

---

# 1. PRIMARY OBJECTIVE

The immediate objective is:

> Make the DCE telemetry representation sufficiently trustworthy and reproducible that real-world RCA experiments can be conducted without silently introducing incorrect timestamp semantics, identities, topology, trace relationships, metric meanings, or incident associations.

After that, establish a reproducible interface to **RCAEval** and determine exactly what information from RCAEval can be represented by the DCE canonical model.

Do NOT yet claim that DCE performs RCA.

Do NOT yet implement the final neural-symbolic RCA architecture.

Do NOT yet implement self-healing, autonomous remediation, causal intervention, or planning.

Those are future research stages.

The immediate goal is to make the **data and experimental substrate trustworthy enough to support them**.

---

# 2. IMPORTANT PROJECT GOVERNANCE

The following experiments already exist and are historical research records.

## E001 — R0 Baseline Reproduction

E001 reproduced the original R0 experiment.

Established:

* the implementation reproduces the delivered R0 results;
* all five comparable metric tables match;
* repository tests passed;
* the experiment is historical/frozen.

Do not modify E001.

Do not rerun E001 as part of this task unless explicitly required for verification.

Do not rewrite its results.

---

## E002 — Timing / Provenance Experiment

E002 investigated whether provenance-aware mixed-source timing relationships improve root-cause ranking over same-source-only timing relationships.

E002-R002 established:

* qualified environment before and after execution;
* 49 tests passed;
* exact repeatability across three repetitions;
* mixed-source policy actually used cross-source timing pairs;
* same-source-only policy used zero cross-source timing pairs;
* candidate generation and thresholds remained unchanged;
* Top-1 performance was identical between mixed and same-source conditions;
* paired Top-1 difference was `0.000`;
* 95% paired bootstrap CI was `[0.000, 0.000]`;
* 237 held-out events;
* the preregistered superiority threshold was not met.

R002 exactly reproduced the R001 raw result.

Therefore:

> E002 does NOT establish hybrid/provenance superiority.

It establishes repeatability and treatment integrity, and shows that the tested synthetic timing/provenance modification did not alter Top-1 ranking under that protocol.

Do not alter E002.

Do not continue modifying E002 to search for a positive result.

Do not reinterpret the null result as proof that provenance/timing is generally useless.

---

# 3. E003 — CURRENT WORKING TARGET

E003 inspected the real telemetry corpus and implemented the initial canonical telemetry representation/replay scaffold.

The current E003 conclusion is:

> The ingestion/normalization/replay infrastructure is useful, but the canonical representation is NOT yet adequate for downstream symbolic RCA or real-world reasoning.

E003 therefore remains a historical adequacy assessment.

Do not overwrite it.

Do not silently convert its historical conclusion into a new conclusion.

Any remediation must be represented as a new explicitly identified run/experiment or amendment according to the repository's experiment governance.

---

# 4. CURRENT E003 FINDINGS YOU MUST PRESERVE

The current E003 corpus contains approximately:

* Bank: ~24.59 GiB expanded
* Market: ~22.90 GiB expanded
* Telecom: ~16.45 GiB expanded
* approximately 63.94 GiB expanded total
* 202 files
* multiple distinct CSV schema families
* 18 telemetry groups
* 6 label/query groups
* 24 distinct system/filename/header groups

The initial adapter successfully mapped real samples, but several semantic problems were found.

The agent MUST treat the following as known issues rather than silently assuming them away.

---

# 5. E003 ISSUE 1 — TIMESTAMP SEMANTICS

Different sources use different timestamp scales and units.

Known observations include:

* Bank/Market metrics/logs use seconds in some files;
* Bank traces contain mixed timestamp behavior;
* Bank traces include both millisecond and second-scale observations across different periods;
* Market traces include millisecond timestamps;
* Telecom metrics/traces include millisecond timestamps;
* `record.csv` labels use seconds;
* some rows fall outside expected source-local windows;
* 2,000 selected Bank rows were rejected;
* 27 rows were outside the relevant source-local window.

The current adapter uses Decimal-based epoch handling and event-time ordering.

However, this is NOT sufficient.

## Required remediation

Build a **file-level timestamp profiling and validation system**.

For every telemetry file or schema group:

1. inspect representative timestamp values;
2. determine candidate timestamp scales;
3. infer the candidate unit;
4. validate that interpretation against:

   * expected date range,
   * neighbouring records,
   * source-local day/window,
   * temporal ordering,
   * known incident labels where appropriate;
5. calculate confidence/evidence for the selected interpretation;
6. record the selected interpretation in provenance;
7. explicitly record ambiguity;
8. reject or quarantine ambiguous data rather than silently converting it.

Do NOT infer timestamp semantics solely from magnitude.

Do NOT use machine ingestion time as a substitute.

Do NOT fabricate timestamps.

The resulting system must distinguish:

```text
validated timestamp interpretation
vs
ambiguous timestamp
vs
invalid timestamp
vs
out-of-window timestamp
```

Rejected rows must remain auditable.

---

# 6. E003 ISSUE 2 — ENTITY / RESOURCE IDENTITY

The initial model does not sufficiently distinguish:

* host
* service
* pod/container
* database
* application component
* other infrastructure resources

Some datasets contain aliases or resource names that need interpretation.

## Required remediation

Create an explicit identity model.

At minimum, support:

```text
Resource
 ├── resource_id
 ├── resource_kind
 ├── canonical_name
 ├── source_name
 ├── namespace/environment if available
 ├── aliases
 └── provenance
```

Possible resource kinds may include:

```text
SERVICE
POD
CONTAINER
HOST
DATABASE
CACHE
QUEUE
APPLICATION
UNKNOWN
```

Do NOT force an entity into a kind when the evidence is insufficient.

Preserve the original source identity.

Create reviewed alias mappings where necessary.

Every identity transformation must be traceable back to source data.

---

# 7. E003 ISSUE 3 — DEPLOYMENT TOPOLOGY

The current graph contains some evidence-backed `CALLS` relationships.

However, deployment topology is incomplete.

A deployment workbook contains explicit host/name relationships, including approximately 201 XML rows.

The initial adapter did not operationally map this deployment information into the graph.

## Required remediation

Build evidence-backed topology relationships such as:

```text
SERVICE
    └── RUNS_ON → POD
                     └── RUNS_ON → HOST

SERVICE
    └── DEPENDS_ON → DATABASE

SERVICE
    └── DEPENDS_ON → CACHE

SERVICE
    └── CALLS → SERVICE
```

Only add a relationship when there is evidence.

Do NOT create generic edges simply because two entities appear in the same dataset.

Do NOT label an edge causal merely because it is topological.

Maintain explicit relation types:

```text
CALLS
DEPENDS_ON
RUNS_ON
READS_FROM
WRITES_TO
HOSTS
```

Potential causal relations must remain distinct from established topology.

---

# 8. E003 ISSUE 4 — TRACE SEMANTICS

Known problems include:

* Bank self-parent spans;
* missing parents;
* incomplete parent resolution;
* Market missing parent/type fields in some records;
* Telecom spans with unresolved parents;
* Telecom serviceName missing initially;
* resource information sometimes available only through fields such as `dsName`.

## Required remediation

Implement explicit trace semantics.

Represent at minimum:

```text
Trace
 ├── trace_id
 ├── root_span_id
 └── spans[]

Span
 ├── trace_id
 ├── span_id
 ├── parent_span_id
 ├── service
 ├── start_time
 ├── end_time
 ├── duration
 ├── status
 ├── attributes
 └── provenance
```

Handle:

* missing parent;
* self-parent;
* multiple possible parent interpretations;
* missing service;
* missing type;
* unresolved parent;
* incomplete trace context.

Do NOT invent missing parents.

Do NOT connect spans solely because they have similar timestamps.

Create explicit unresolved states.

Implement bounded trace-context retrieval rather than assuming that every trace can be reconstructed completely.

---

# 9. E003 ISSUE 5 — METRIC SEMANTICS

The current representation expands wide telemetry into observations, but semantic information is incomplete.

You must not assume that every numeric column means the same thing.

Create a metric semantics registry.

At minimum capture:

```text
metric_name
source_metric_name
unit
temporality
aggregation
kind
description/status
source
provenance
```

Distinguish concepts such as:

```text
GAUGE
COUNTER
RATE
HISTOGRAM
DURATION
LATENCY
COUNT
UNKNOWN
```

If the source semantics are unknown:

```text
temporality = UNKNOWN
unit = UNKNOWN
```

Do not fabricate semantics.

Document how wide-format metrics are interpreted.

Document duration units.

Document status encodings.

Document whether values are cumulative, instantaneous, sampled, or derived.

---

# 10. E003 ISSUE 6 — COVERAGE / SCALE

The full corpus has not yet been exhaustively profiled.

The current E003 numbers are useful but are NOT equivalent to complete population statistics.

Known sampled/processed observations included approximately:

* 100,763 scanned rows
* 98,736 mapped rows
* 2,000 rejected rows
* 27 outside-window rows
* 103,008 metric observations
* 20,000 logs
* 13,984 spans
* 3,403 `CALLS` evidence edges

These values must not be represented as full-dataset totals unless independently verified.

## Required remediation

Perform a scalable coverage audit.

For every file/source/system:

Record:

```text
file size
row count
mapped count
rejected count
ambiguous count
out-of-window count
duplicate count
missingness
timestamp range
timestamp scale
metric/schema groups
entity counts
trace counts
span counts
label counts
```

Also measure:

```text
memory usage
processing time
throughput
peak memory
```

Do not load the entire 64 GiB corpus into memory.

Use streaming/chunked processing where appropriate.

If full processing is too expensive, explicitly state the limitation and produce a statistically/operationally justified sampling strategy.

---

# 11. E003 ISSUE 7 — INCIDENT / LABEL SEMANTICS

Current labels behave as point-fault annotations.

Examples include incident identifiers such as:

```text
scenario@record.csv logical line
```

The label system provides root-cause information but does not necessarily provide a complete incident interval.

Known information includes:

* root entity;
* fault scenario;
* injection/label point;
* day scope.

Unknown in many cases:

```text
fault_end_time
incident_end_time
true recovery_time
```

## Required remediation

Separate:

```text
FaultEvent
Incident
GroundTruth
QueryWindow
```

For example:

```text
FaultEvent
 ├── start_time
 ├── target
 ├── fault_type
 └── source

Incident
 ├── incident_id
 ├── query_window
 ├── associated_faults
 └── metadata

GroundTruth
 ├── root_cause_entity
 ├── root_cause_indicator
 ├── fault_type
 └── injection_time
```

Do not fabricate an end time.

Do not redefine evaluator-owned association rules.

The evaluator's ground truth must remain separate from the system's inferred graph.

---

# 12. IMPORTANT PRINCIPLE — OBSERVATION ≠ CAUSALITY

The DCE model must preserve three distinct concepts:

```text
OBSERVED
POSSIBLE RELATION
ESTABLISHED CAUSAL RELATION
```

For example:

```text
Service A CALLS Service B
```

does NOT mean:

```text
A caused B's failure.
```

Similarly:

```text
CPU spike happened before latency spike
```

does NOT automatically establish:

```text
CPU spike caused latency spike.
```

This distinction is fundamental to the project.

---

# 13. REQUIRED DCE CANONICAL TELEMETRY MODEL

The remediation should converge toward a representation capable of expressing:

```text
MetricObservation
LogEvent
TraceSpan
Resource
Dependency
FaultEvent
Incident
GroundTruth
```

A minimal conceptual representation is:

```text
MetricObservation
    timestamp
    resource_id
    metric_name
    value
    unit
    temporality
    source
    attributes
    provenance
    quality

LogEvent
    timestamp
    resource_id
    severity
    message
    attributes
    source
    provenance

TraceSpan
    trace_id
    span_id
    parent_span_id
    resource_id
    start_time
    end_time
    duration
    status
    attributes
    provenance

Dependency
    source
    target
    relation_type
    evidence
    provenance

FaultEvent
    timestamp
    target
    fault_type
    parameters
    provenance

GroundTruth
    incident_id
    root_cause
    root_cause_indicator
    fault_type
    injection_time
    source
```

This is a target representation, not permission to invent semantics.

---

# 14. REPOSITORY ARCHITECTURE REQUIREMENTS

Maintain clean separation between:

```text
domain model
ingestion
normalization
dataset adapters
replay
evaluation
experiments
CLI
visualization
```

Domain modules must NOT directly depend on:

* FastAPI
* UI
* broker-specific APIs
* notebook state
* arbitrary filesystem paths
* benchmark-specific implementation details

Adapters should translate source-specific data into the canonical representation.

The canonical representation must not become a copy of RCAEval's internal schema.

---

# 15. RCAEval — NEXT REAL-WORLD TARGET

After E003 remediation reaches the defined adequacy gate, integrate RCAEval.

Use the current RCAEval repository/release as the authoritative source rather than relying on remembered descriptions.

Current RCAEval provides:

* nine datasets;
* 735 real failure cases;
* 11 fault types;
* systems including:

  * Online Boutique
  * Sock Shop
  * Train Ticket;
* multiple evaluation settings;
* metric-only and multi-source scenarios;
* root-cause service;
* root-cause indicator;
* injection time;
* reproducible RCA baselines.

The repository currently provides lossless Parquet distribution and a case index, allowing case-by-case or suite-by-suite access.

Use the official repository/documentation and record the exact version/commit/release used.

---

# 16. RCAEval INTEGRATION MUST START SMALL

Do NOT immediately download/process all data.

First determine:

1. exact RCAEval version;
2. exact dataset list;
3. exact schema;
4. exact evaluation protocol;
5. exact ground-truth representation;
6. exact telemetry modalities available;
7. exact baseline implementations;
8. exact data licensing/access requirements;
9. storage requirements;
10. compute requirements.

Prefer a small representative subset first.

The agent must produce a dataset inventory before bulk ingestion.

---

# 17. RCAEval DATASET INVENTORY

Create a machine-readable inventory containing at minimum:

```text
dataset
suite
case_id
system
fault_type
root_cause_service
root_cause_indicator
injection_time
telemetry_modalities
metric availability
log availability
trace availability
code/source availability if applicable
dataset size
local availability
download location
checksum if available
```

Do not guess values.

Unknown values must be explicitly represented as unknown.

---

# 18. RCAEval → DCE MAPPING

For a small representative RCAEval subset, implement a reversible mapping:

```text
RCAEval source
      ↓
DCE adapter
      ↓
Canonical telemetry
      ↓
DCE graph/evidence representation
```

The mapping must preserve source provenance.

For every canonical object, it must be possible to answer:

> Which source record(s) produced this object?

Likewise, for every source record:

> What happened to it?

Possible states:

```text
mapped
rejected
ambiguous
unsupported
out_of_window
```

Do not silently drop records.

---

# 19. BIDIRECTIONAL TRACEABILITY

Implement enough provenance to support:

```text
source record
    ↓
canonical object
    ↓
graph/evidence object
    ↓
RCA query
    ↓
evaluation result
```

This is necessary because later RCA failures must be distinguishable between:

```text
dataset problem
adapter problem
representation problem
candidate-generation problem
ranking problem
evaluation problem
```

---

# 20. RCAEval GROUND TRUTH MUST REMAIN EXTERNAL

Do NOT inject RCAEval ground truth into the evidence graph used for RCA.

The system may store ground truth separately for evaluation.

Correct:

```text
telemetry → DCE evidence graph
                         ↓
                    RCA system
                         ↓
                  predicted root cause
                         ↓
                external evaluator
                         ↑
                    ground truth
```

Incorrect:

```text
ground truth → evidence graph → RCA prediction
```

Ground truth must never leak into model features, graph construction, candidate ranking, or explanations.

---

# 21. DATA LEAKAGE AUDIT

Before any RCA evaluation, explicitly check for:

* root-cause labels in telemetry fields;
* fault identifiers embedded in filenames;
* incident identifiers embedded in paths;
* injection metadata accidentally exposed to inference;
* benchmark-specific metadata;
* future information relative to the query time;
* evaluation labels accidentally used during candidate generation;
* source ordering that reveals the answer.

Produce a leakage report.

If leakage is found:

1. document it;
2. determine whether it can be removed;
3. quarantine the affected field;
4. do not continue as if the benchmark were valid.

---

# 22. TEMPORAL CAUSALITY / LOOK-AHEAD RULE

For any future RCA experiment, establish an explicit observation window.

Example:

```text
incident/query time = T
available telemetry = [T - W, T]
```

Do not allow:

```text
telemetry after T
```

unless the experiment explicitly defines a post-event diagnosis task.

Every RCA experiment must specify:

```text
query_time
observation_window
allowed modalities
future-information policy
```

---

# 23. FIRST RCAEval EXPERIMENT SHOULD NOT BE A NEW MODEL

The first RCAEval experiment should answer:

> Can DCE ingest, normalize, represent, replay, and evaluate real RCA telemetry without semantic or provenance corruption?

This is an infrastructure/representation validation experiment.

Only after this succeeds should we reproduce an established RCA baseline.

Only after baseline reproduction should we introduce DCE-specific symbolic reasoning.

---

# 24. PROPOSED EXPERIMENTAL SEQUENCE

Do NOT automatically create these IDs unless the repository's experiment register authorizes them.

Treat the following as the intended sequence:

```text
E003 remediation
      ↓
real telemetry adequacy gate
      ↓
RCAEval ingestion/representation validation
      ↓
RCAEval baseline reproduction
      ↓
DCE symbolic RCA baseline
      ↓
multi-source evidence experiments
      ↓
neural + symbolic evidence fusion
      ↓
real-world RCA evaluation
      ↓
AIOpsLab controlled fault injection
      ↓
causal intervention experiments
      ↓
safe planning/remediation
```

Do not skip stages.

---

# 25. AIOpsLab IS A FUTURE EXPERIMENTAL ENVIRONMENT

AIOpsLab should NOT be treated as merely another static dataset.

Its role is later:

```text
deploy distributed system
        ↓
generate workload
        ↓
inject controlled fault
        ↓
collect telemetry
        ↓
perform RCA
        ↓
recommend remediation
        ↓
execute controlled intervention
        ↓
verify recovery
```

Do not integrate AIOpsLab into this task unless required to validate an interface.

It belongs after real-world RCA evaluation.

---

# 26. EXPERIMENT GOVERNANCE

Every new experiment/run must contain appropriate records such as:

```text
README.md
hypothesis.md
protocol.md
configuration.yaml
run.md
results/
logs/
decision.md
```

Use the repository's established experiment conventions.

Each run must preserve:

* exact configuration;
* code/runner version;
* dependency/environment information;
* dataset version;
* dataset checksums where available;
* input subset;
* execution command;
* output hashes;
* logs;
* test results;
* known limitations;
* decision.

Never overwrite historical results.

---

# 27. HARD RULE — NO RESULT HUNTING

Do not modify the protocol because the result is inconvenient.

Do not:

* tune until RCA improves;
* silently remove difficult cases;
* change thresholds after seeing results;
* remove ambiguous records without recording them;
* change ground truth;
* change observation windows after inspecting outcomes;
* cherry-pick datasets;
* selectively report successful cases.

If a result is null, negative, or ambiguous:

> record it.

The purpose is to learn what the system actually establishes.

---

# 28. TESTING REQUIREMENTS

Every remediation must add or update automated tests for:

### Timestamp tests

* seconds;
* milliseconds;
* nanoseconds if present;
* ambiguous scale;
* invalid timestamp;
* out-of-window timestamp;
* mixed timestamp files.

### Identity tests

* service;
* pod;
* host;
* database;
* alias;
* unknown resource.

### Trace tests

* valid parent;
* missing parent;
* self-parent;
* missing service;
* unresolved parent.

### Topology tests

* CALLS;
* RUNS_ON;
* DEPENDS_ON;
* no fabricated causal edges.

### Metric tests

* gauge;
* counter;
* duration;
* unknown semantics.

### Provenance tests

Every mapped object must retain source provenance.

### Leakage tests

Ground-truth fields must not reach inference inputs.

### Determinism tests

Repeated normalization of the same input must produce identical canonical output.

---

# 29. REQUIRED VALIDATION GATES

Do not declare E003 remediation complete until the following are evaluated.

## Gate A — Timestamp Integrity

PASS only if:

* timestamp interpretation is explicit;
* validated per file/schema group;
* ambiguous cases are represented as ambiguous/rejected;
* no fabricated timestamps;
* source-local windows behave correctly.

---

## Gate B — Identity Integrity

PASS only if:

* resources have explicit kinds;
* aliases are documented;
* source identity is preserved;
* unknown identity is not silently coerced.

---

## Gate C — Topology Integrity

PASS only if:

* deployment relationships are evidence-backed;
* CALLS relationships are trace-derived;
* missing relationships remain missing;
* causal semantics are not conflated with topology.

---

## Gate D — Trace Integrity

PASS only if:

* parent semantics are explicit;
* self-parent cases are handled;
* missing parents are represented;
* unresolved traces do not produce fabricated structure.

---

## Gate E — Metric Semantics

PASS only if:

* units/temporality are explicit where known;
* unknown semantics remain unknown;
* metric transformations are documented.

---

## Gate F — Coverage

PASS only if:

* processing coverage is measurable;
* rejected/ambiguous rows are counted;
* duplicates/missingness are measurable;
* scalability characteristics are documented.

---

## Gate G — Ground Truth Isolation

PASS only if:

* evaluator labels remain separate;
* no label leakage occurs;
* query-time future information is controlled.

---

## Gate H — Deterministic Replay

PASS only if:

Repeated processing of identical inputs yields identical canonical representations and hashes.

---

# 30. REQUIRED DELIVERABLES

At the end of the task, produce:

## 1. E003 remediation implementation

Code implementing the approved semantic fixes.

---

## 2. Data profiling tools

Commands capable of producing:

```text
timestamp profile
schema profile
identity profile
trace profile
topology profile
missingness profile
duplicate profile
coverage profile
```

---

## 3. Machine-readable reports

Prefer JSON/JSONL/CSV where appropriate.

---

## 4. Canonical schema documentation

Explain:

```text
what each object means
what is known
what is unknown
what is inferred
what is source-derived
```

---

## 5. Provenance documentation

Document source-to-canonical mappings.

---

## 6. RCAEval inventory

Record the exact version and available datasets/cases.

---

## 7. RCAEval representative subset

Do NOT download the full corpus unless necessary.

Use a controlled representative subset first.

---

## 8. RCAEval → DCE adapter

Implement source-to-canonical conversion.

---

## 9. Leakage audit

Explicitly demonstrate that evaluation ground truth does not enter inference.

---

## 10. Validation report

Report each gate:

```text
PASS
FAIL
PARTIAL
NOT TESTED
```

Do not convert PARTIAL into PASS.

---

## 11. Experiment record

Create the appropriate experiment/run artifacts using the repository's established governance.

---

## 12. Decision record

The decision must state one of:

```text
ACCEPT
REVISE
REJECT
BLOCKED
```

and explain why.

---

# 31. STOP CONDITIONS

The agent MUST stop and request review if:

### Stop condition 1

The timestamp semantics cannot be resolved reliably.

### Stop condition 2

The dataset schema is ambiguous enough that canonicalization would require unsupported assumptions.

### Stop condition 3

Ground-truth leakage cannot be ruled out.

### Stop condition 4

RCAEval data cannot be mapped without losing critical semantics.

### Stop condition 5

A proposed mapping would require inventing topology, identity, causality, or timestamps.

### Stop condition 6

A change would modify historical E001/E002/E003 results.

### Stop condition 7

A new experiment would require changing the preregistered protocol.

### Stop condition 8

The full dataset cannot be processed safely within available resources.

In these cases:

```text
DO NOT WORK AROUND THE PROBLEM SILENTLY.
DOCUMENT IT.
STOP.
REQUEST REVIEW.
```

---

# 32. WHAT YOU MUST NOT DO

Do NOT:

* modify E001 historical results;
* modify E002 historical results;
* erase failed runs;
* overwrite old experiment artifacts;
* invent timestamps;
* infer causality from correlation;
* invent missing trace parents;
* invent deployment topology;
* inject ground truth into inference;
* use future telemetry without explicit protocol authorization;
* build the final neural-symbolic model yet;
* claim RCA capability before validation;
* claim causal reasoning before causal experiments;
* claim self-healing before intervention experiments;
* download the entire RCAEval corpus unnecessarily;
* optimize for a positive benchmark result;
* silently discard inconvenient data.

---

# 33. IMPORTANT DISTINCTION: WHAT WE ARE BUILDING NOW

The immediate architecture is:

```text
                    REAL TELEMETRY
                         │
                         ▼
                Dataset-specific adapters
                         │
                         ▼
              Timestamp / schema validation
                         │
                         ▼
                Canonical DCE telemetry
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
          Metrics       Logs       Traces
             │           │           │
             └───────────┼───────────┘
                         ▼
                 Resource identity
                         │
                         ▼
                Evidence-backed topology
                         │
                         ▼
                 Temporal replay/query
                         │
                         ▼
              RCA-ready evidence substrate
                         │
                         ▼
                    RCAEval evaluator
```

The future architecture is:

```text
RCA-ready evidence
        │
        ├──────────────► Neural evidence model
        │
        └──────────────► Symbolic reasoning
                              │
                              ▼
                       Evidence fusion
                              │
                              ▼
                       RCA ranking
                              │
                              ▼
                         Explanation
                              │
                              ▼
                     Causal reasoning
                              │
                              ▼
                       Counterfactual
                              │
                              ▼
                         Planning
                              │
                              ▼
                    Safety verification
                              │
                              ▼
                     Controlled action
                              │
                              ▼
                         Verification
```

The second architecture is NOT the current implementation target.

---

# 34. SUCCESS CRITERION

The task is successful if another researcher can take:

```text
the documented dataset version
+
the documented configuration
+
the documented code version
```

and independently determine:

1. what telemetry was available;
2. how timestamps were interpreted;
3. how resources were identified;
4. how traces were reconstructed;
5. how topology was constructed;
6. which records were rejected;
7. what information was unknown;
8. what ground truth existed;
9. what information was exposed to RCA;
10. what was evaluated;
11. what result was obtained.

The strongest outcome is NOT necessarily better RCA accuracy.

The strongest outcome is:

> a trustworthy, reproducible, leakage-controlled real-world RCA substrate on which later symbolic, neural, causal, and self-healing experiments can be scientifically evaluated.

---

# 35. EXECUTION ORDER

Execute in this order:

```text
PHASE 0
Read repository governance and experiment registry.

PHASE 1
Inspect current E003 implementation and artifacts.

PHASE 2
Create remediation protocol.

PHASE 3
Implement timestamp profiling/validation.

PHASE 4
Implement resource identity normalization.

PHASE 5
Implement deployment topology mapping.

PHASE 6
Implement trace semantic handling.

PHASE 7
Implement metric semantics registry.

PHASE 8
Implement coverage/scalability profiling.

PHASE 9
Implement incident/ground-truth separation.

PHASE 10
Add provenance and leakage tests.

PHASE 11
Run E003 remediation validation.

PHASE 12
Evaluate all remediation gates.

IF ANY CRITICAL GATE FAILS:
    stop
    document failure
    request review

IF ADEQUACY GATE PASSES:
    proceed to RCAEval discovery.

PHASE 13
Record exact RCAEval version/release/commit.

PHASE 14
Inventory datasets and schemas.

PHASE 15
Select a small representative subset.

PHASE 16
Implement RCAEval → DCE adapter.

PHASE 17
Run round-trip/provenance validation.

PHASE 18
Run leakage audit.

PHASE 19
Evaluate DCE representation against RCAEval ground truth metadata
WITHOUT using ground truth during inference.

PHASE 20
Produce decision report.

STOP.

Do NOT automatically proceed to baseline reproduction or model development.
```

---

# 36. FINAL REPORT FORMAT

The final report must contain:

```text
# Executive Summary

# What Changed

# What Was Previously Known

# E003 Problems Addressed

# Problems Still Unresolved

# Timestamp Semantics

# Identity Semantics

# Topology Semantics

# Trace Semantics

# Metric Semantics

# Coverage / Scalability

# Ground Truth Model

# Provenance

# Leakage Audit

# RCAEval Version

# RCAEval Dataset Inventory

# RCAEval → DCE Mapping

# Validation Results

# Gate Results

# Tests

# Reproducibility

# Limitations

# Decision

# Recommended Next Experiment
```

The final section must NOT automatically authorize the next experiment.

It should recommend the next logical research question and wait for human approval.

---

# 37. CORE RESEARCH PRINCIPLE

Throughout the task, maintain this discipline:

```text
DATA
  ↓
OBSERVATION
  ↓
REPRESENTATION
  ↓
EVIDENCE
  ↓
REASONING
  ↓
CONCLUSION
```

Never silently jump:

```text
DATA → CAUSALITY
```

Never silently jump:

```text
CORRELATION → ROOT CAUSE
```

Never silently jump:

```text
BENCHMARK LABEL → MODEL INPUT
```

Never silently jump:

```text
EXPERIMENT RESULT → GENERAL SYSTEM CLAIM
```

Every transition must be explicit, testable, and recorded.

The objective is to build DCE as a **research-grade distributed AI reasoning system**, not a benchmark-specific demo.
