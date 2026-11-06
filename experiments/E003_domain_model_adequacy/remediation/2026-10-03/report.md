# Executive Summary

E003-AM001 implements and validates a separate v2 representation. It improves timestamp handling, deployment topology, trace-reference states, exact numeric preservation and source-row auditability. The downstream adequacy decision remains **REVISE**, pending human review. RCAEval remains behind the adequacy gate.

The validation covers all four scenarios and all 162 telemetry CSV files, using a deterministic prefix of up to 512 rows per file. All 335 fault annotations and 335 query rows are read separately for evaluation. These are bounded telemetry measurements, not full incident or full population results.

# What Changed

New code in `src/dce_foundation/representation_v2/` provides domain values, per-file time evidence, strict source mappings, typed resources, a metric registry, explicit parent states, workbook topology, disk-backed dispositions and deterministic replay. Tests challenge source interpretation and storage end to end. Original v1 code and historical experiment records are preserved.

# What Was Previously Known

E001 reproduced R0. E002 reproduced its null performance difference under a qualified environment. E003-R001 mapped bounded samples but found inconsistent Bank trace scales, missing workbook topology, unknown semantics, incomplete trace context and insufficient incident coverage. Those results retain their original meaning.

# E003 Problems Addressed

Timestamp scales now require date evidence. Source rows have explicit outcomes. Workbook Host/Name pairs create operational RUNS_ON edges. Resources preserve evidence-backed kinds without alias merging. Missing/self/ambiguous trace parents produce explicit states. Metric values retain exact strings. Labels, query scoring points and inferred operational evidence have separate storage and APIs.

# Problems Still Unresolved

Whole-file time interpretation, incident-centered coverage, source-backed metric/duration/status semantics, reviewed container aliases, deployment validity intervals, official query-to-fault association, comprehensive benchmark-cue leakage checks and query-time graph filtering remain incomplete. No full 64 GiB scan or production ingestion qualification is claimed.

# Timestamp Semantics

Candidate seconds/milliseconds/microseconds/nanoseconds interpretations must match the source-local UTC+08 day with a fixed one-hour allowance during profiling. Mapping then uses strict day bounds. Magnitude alone cannot select a unit. Mixed candidate scales are quarantined as ambiguous; malformed timestamps are rejected; valid timestamps outside the day are kept as out_of_window evidence.

All 162 sampled files have a uniquely supported interpretation: 61 seconds, 101 milliseconds. Bank traces for March 4–12 support milliseconds; March 23–25 support seconds. These are file-prefix findings, not proof of uniform scales throughout each file. The fixed allowance does not silently import boundary rows into the day: 908 sampled Bank rows are outside the strict window.

# Identity Semantics

IDs hash environment plus exact source identity. No punctuation-based typing or automatic identity normalization is performed. The final corrected workbook handling preserves HOST evidence from Host-column references even when a later named row has an unrecognized type. Namespace and aliases remain absent/unknown unless documented. Source names survive in resource/provenance storage.

V002's workbook implementation downgraded seven supported HOST resources to UNKNOWN. That engineering defect is documented in logs/V002-review.md; V003 corrects it. The prior snapshot/results remain intact.

# Topology Semantics

The sampled graph contains 4,343 CALLS evidence edges and 20 RUNS_ON edges. CALLS requires a unique same-environment, same-trace parent identity. RUNS_ON requires explicit workbook Host/Name cells. Workbook merged values propagate only inside declared same-column merge ranges; heading merges are not extrapolated. Five container hints remain unreviewed candidates. No DEPENDS_ON, READS_FROM, WRITES_TO or HOSTS relation is invented merely because the model supports that type. None of these edges is a causal claim.

# Trace Semantics

14,028 spans are mapped. Parent states: 4,343 resolved, 9,372 unresolved, 210 self-parent conventions unknown, and 103 missing-parent/root-meaning-unknown. Missing service/type fields are recorded. Duration values and status tokens survive exactly, while end times, duration units and interpreted status remain unknown. Resolution is bounded by the selected context; unresolved does not mean a real dependency is absent.

# Metric Semantics

95,748 metric observations are represented. Numeric source strings are retained without float rounding; Decimal checks finite validity. Wide rows expand into separately named observations. Unit, temporality, aggregation and kind remain UNKNOWN when source documentation is insufficient. Registry declarations require source evidence. Counter/gauge/duration semantics are fixture-tested but are not fabricated for OpenRCA acronyms.

# Coverage / Scalability

| Scenario | Telemetry files | Sampled rows | Mapped rows | Outside day |
|---|---:|---:|---:|---:|
| Bank | 40 | 20,480 | 19,572 | 908 |
| Market/cloudbed-1 | 16 | 8,192 | 8,192 | 0 |
| Market/cloudbed-2 | 16 | 8,192 | 8,192 | 0 |
| Telecom | 90 | 44,249 | 44,249 | 0 |
| Total | 162 | 81,113 | 80,205 | 908 |

Conservation holds for every file. There are no timestamp-ambiguous, rejected or unsupported sampled rows in the completed validation; two exact duplicate source rows are counted and retained. Canonical expansion yields 118,992 observations: 95,748 metrics, 9,216 logs and 14,028 spans.

The first V003 telemetry pass took approximately 62.2 seconds, about 1,303 sampled rows/second, with a measured process peak working set of approximately 60.5 MiB. Its SQLite artifact is 321,150,976 bytes. These measurements describe this prefix workload and exclude archive hashing and the separate incident-coverage evaluation. Complete performance values for both passes are in coverage-*.json. Record counts for capped files are explicitly unknown; a file that reaches EOF has its observed complete count recorded. No extrapolated whole-corpus throughput or RAM claim is made.

The prefix census screens every schema/day cheaply; it is not random or statistically representative. Of 335 labelled faults, 283 roots appear somewhere in the sampled resource graph, but only 8 have any sampled root telemetry within five minutes of the labelled point. Prefix absence cannot invalidate a label or establish unavailable source telemetry. Deviation visibility is NOT TESTED because this task does not introduce anomaly detection.

# Ground Truth Model

FaultEvent is a point annotation with unknown end. Incident stores an evaluator association, which remains UNKNOWN for query/fault matching. GroundTruth retains root identity, reason and injection point. OpenRCA record/query rows are stored in evaluation-only.sqlite, never opened by the telemetry pass. All 335 epoch/datetime label comparisons agree under UTC+08; no incident interval or recovery time is invented.

# Provenance

Preflight records commit `319b50f564027fc0fac2503c4656e703a741c318`, dirty state, exact interpreter/dependencies, code/configuration hashes and a source ZIP snapshot before processing. Dataset-provenance.json hashes the actual raw archives and records unknown upstream version. Original attachment bytes have SHA-256 `ee3be2a13b2bab454bb47a5923b999b47be95faa027b8917353b14e0003d0343`; execution-brief.md is its UTF-8 text archive with normalized file formatting.

Source catalog plus dispositions reconstruct every canonical object's originating logical record. Accepted, rejected, ambiguous, unsupported and out-of-window records retain raw fields. CSV byte layout is recoverable from raw archives, not canonical serialization. See provenance-and-mappings.md and artifact-manifest.json.

# Leakage Audit

Explicit evaluation labels are isolated. Inference projection omits paths, source row order, raw attributes, fault/query metadata and log text. QueryWindow excludes observations after its cutoff. Fixture tests challenge answer-bearing log fields and future timestamps.

Gate G remains PARTIAL: complete metric/resource/trace-name benchmark-cue checks, evaluator association rules and query-time edge/context filtering are not qualified. Operational replay with raw provenance is an audit API, not an inference API. No ranking or diagnosis is evaluated from it.

# RCAEval Version

NOT TESTED. Discovery follows the all-A–H adequacy gate in the user's execution brief. The gate is not passed, so no current commit/release is asserted from memory or from the prompt's descriptive counts.

# RCAEval Dataset Inventory

NOT STARTED. No case inventory or full-corpus download is fabricated. A real versioned inventory is a deferred conditional deliverable.

# RCAEval → DCE Mapping

NOT STARTED. Adapter/subset/round-trip/evaluator work follows adequacy review and the explicitly authorized conditional scope.

# Validation Results

V001: retained engineering failure (SQLite resource_id column missing). V002: completed repeated validation, with a subsequently identified workbook kind-preservation defect documented separately. V003: corrected engineering validation using the unchanged sampling/window/gate configuration. No unfavorable cases, failed attempts or historical results were overwritten.

# Gate Results

| Gate | Result | Reason |
|---|---|---|
| A Timestamp integrity | PARTIAL | Sample interpretation is explicit; whole-file uniformity remains unverified. |
| B Identity integrity | PASS within tested scope | Exact names, scoped kinds, explicit UNKNOWN, no unreviewed alias coercion. |
| C Topology integrity | PASS within tested scope | Source-backed workbook and parent evidence; missing relations retained as missing. |
| D Trace integrity | PASS within tested scope | Unresolved/self/missing parent states explicit; no invented structure. |
| E Metric semantics | PARTIAL | Source meanings remain unknown despite representation/registry support. |
| F Coverage | PARTIAL | Measurable prefix census and bounded memory; incident/full-population adequacy unverified. |
| G Ground truth isolation | PARTIAL | Structural isolation tested; full content/look-ahead audit unfinished. |
| H Deterministic replay | PASS within tested scope | Two independent passes have identical canonical hashes and graph digests. |

Passing an integrity condition within the bounded sample does not qualify the full dataset. All gates must pass before downstream advancement.

# Tests

76 repository tests passed in 2.84 seconds, including 27 new tests. Coverage includes timestamp scales/mixed scales/boundaries/invalid precision, all resource kinds, aliases/unknown identities, source-backed metric declarations, raw precision, parent references, topology evidence, missing semantics, leakage/future exclusions, merged workbook cells, disk pipeline conservation, duplicates and repeated hashes. The initial classifier failure and sandbox temp-directory failure are documented in implementation-checkpoints.md.

# Reproducibility

Use commands.md and a new output directory. Each executed attempt has its own source snapshot, exact configuration and raw artifacts. Both V003 passes have canonical SHA-256 `7b3b7ceb271c7be439c6c137e91363e3a96b77a0daad9e5da350e6edddb0a8e0` and graph SHA-256 `4465ef648384cbe0db6989716ba25a107b4995ce9fdf050a93f966ed507f2135`. No overwrite is allowed. This is local artifact-based repeatability, not hosted immutable storage or a clean committed release. The interpreter uses the previously qualified local virtual environment with inherited pinned packages; portable wheel reconstruction remains outside this evidence.

# Limitations

Prefix bias, incomplete span context, unknown source version/licensing provenance, unknown metric/duration meanings, no original evaluator association, incomplete inference graph filtering and whole-corpus processing remain explicit. The audit CLI implements the bounded protocol; disk-backed persistence alone does not prove full-volume scalability. No RCA model, baseline reproduction, causal reasoning, planning or self-healing capability is established.

# Decision

**REVISE — pending human review.** Accepting the engineering work would acknowledge improved auditability and tested semantic handling. It would not approve downstream adequacy. The all-pass gate remains unmet and RCAEval is deferred according to the execution brief.

# Recommended Next Experiment

Recommend reviewing a separately registered incident-centered context/coverage and leakage protocol, together with source-backed metric/duration semantics and evaluator query association. Measure complete near-event resource/trace coverage and permitted inference inputs before benchmark or ranking work. This recommendation does not allocate a new E-number or authorize execution.
