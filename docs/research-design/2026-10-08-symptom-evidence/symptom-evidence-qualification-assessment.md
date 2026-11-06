# Symptom-evidence qualification assessment

Date: 8 October 2026, Asia/Calcutta. Authority: the user's attached design/review instructions. This is an additive diagnostic assessment, not an experiment result, registration, review approval or new execution protocol.

**STATUS: NOT SUPPORTED for execution with the currently established evidence.** The retained telemetry can be inventoried and replayed, but the records do not establish qualified metric semantics or a defensible healthy reference for the proposed symptom question. This does not prove the raw telemetry has no useful signal. It means that choosing and evaluating a detector now would require unsupported assumptions.

The attachment explicitly requires stopping for ambiguous semantics or missing healthy controls. Accordingly, no detector was implemented and no experiment proposal was created. A preregistration-style method, calibration choice or numerical acceptance threshold would be premature.

## 1. What was inspected

Repository governance and dated approvals; the E003 original and AM002 protocols/configuration/boundary records; V006 summary, metric registry, retained source profiles, coverage inventory and context reference; E004 frozen protocol and run-specific results/decision; the scientific telemetry/time/reasoning/evaluation contracts; source profiling and inference projection code; the dated progress report.

Source roots: `experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V006/`, `src/dce_foundation/qualification/`, and `experiments/E004_symbolic_rca_baseline/`. Hashes and derived counts are supplied in the accompanying inventory and inspection files. These derived counts describe existing artifacts; they are not a new scientific execution.

No raw ZIP, cloud dataset, retained context database or compressed replay payload was opened. No signal distribution, threshold, anomaly policy, new window, prediction or ranking was computed. The lack of those operations limits this assessment to available metadata, existing results and implementation evidence.

## 2. What telemetry exists

| Evidence family | Available structure | Scientific boundary |
|---|---|---|
| Source systems | Bank, Market/cloudbed-1, Market/cloudbed-2, Telecom | Environment scopes are not interchangeable reference populations |
| Metrics | Long tables with source identity/name/value and wide application tables | Names are identifiers, not evidence of units or physical meaning |
| Bank wide values | `rr`, `sr`, `cnt`, `mrt`, keyed by `tc` | Acronym expansions and units remain UNKNOWN |
| Market wide values | `rr`, `sr`, `mrt`, `count`, keyed by `service` | Numeric representation is not qualified rate/count/latency meaning |
| Telecom wide values | `avg_time`, `num`, `succee_num`, `succee_rate`, keyed by `serviceName` | Names alone cannot authorize timing, counters or success rates |
| Long metric examples | `container_cpu_usage_seconds`, `container_cpu_used`; Bank names may contain resource tokens | No canonical unit, counter reset or service mapping is inferred from spelling |
| Time | Recorded source timestamps; inherited whole-file scale profiles and nanosecond projection bounds | Scale qualification is not clock accuracy, receipt latency, regular sampling or fresh B/D retesting |
| Traces | Trace/span/parent identifiers, raw duration/elapsed fields, source resource identity | Duration units and success/status meaning UNKNOWN; incomplete/ambiguous parents remain explicit |
| Logs | Bank and Market log source files | Inference projection excludes text and uses UNKNOWN severity plus message-availability flag; Telecom logs are not represented in these retained profiles |
| Topology | CALLS edges supported by resolved same-trace span parents inside the window | Partial observed dependency structure, not complete topology or causality; workbook temporal validity UNKNOWN and excluded |
| Evaluator records | Point fault annotations, roots/reasons, queries/scoring points and coverage | Evaluation-only; not symptom inputs or healthy-state certificates |

Stored profiles comprise 162 inherited source files: 115 metric, 29 span and 18 log files. Their inherited row counts total 523,947,689; this assessment did not read those rows. V006 marks all 162 timestamp profiles QUALIFIED, with conservation and CRC-to-EOF flags. These are inherited records, not a new raw verification of B or D.

The registry has **7,956 source-specific entries and 1,808 distinct (scenario, metric-name) pairs**. These are different counting units; neither is a certified catalogue of distinct physical features. Scenario entry counts: Bank 3,630; Market/cloudbed-1 1,170; Market/cloudbed-2 1,174; Telecom 1,982.

The preserved annotation inventory has 335 cases: Bank 136; Market/cloudbed-1 70; Market/cloudbed-2 78; Telecom 51. None is declared a normal-control case by this assessment.

## 3. What is semantically trustworthy, and what is UNKNOWN

The current registry contains **zero QUALIFIED entries and 7,956 UNKNOWN entries**, each with null semantic evidence and zero asserted confidence. All registry unit/kind/temporality/aggregation fields are UNKNOWN. This is directly checked against the artifact, not copied from the prompt.

| Property | Current classification | Consequence |
|---|---|---|
| Exact source metric-name identity | KNOWN source string | Can inventory and link provenance; physical meaning may be unknown |
| Physical metric identity / service mapping | UNKNOWN unless separately evidenced; no such qualification in this inventory | Do not merge names, infer pod-service aliases or treat root labels as mappings |
| Source | KNOWN retained scenario/path/profile | Source provenance supports inspection, not biological/operational meaning |
| Unit | UNKNOWN | No unit conversions or claimed physical threshold |
| Semantic meaning / kind | UNKNOWN | No asserted CPU utilization, error rate, latency or counter solely from names |
| Sampling behavior | UNKNOWN as a qualified per-series policy | File order and timestamp scale do not certify regular cadence |
| Temporality | UNKNOWN | No rate/delta derivation assuming a cumulative counter |
| Reset behavior | UNKNOWN | No blanket not-applicable classification; gauge/counter status is unresolved |
| Missingness semantics | UNKNOWN | Missing or zero cannot automatically mean healthy, failed, absent or imputed |
| Aggregation semantics | UNKNOWN | No combining percentiles, rates or instance samples without a contract |

**Safe today:** source-linked inventory, exact-name accounting, inherited timestamp-scale reporting, replay conservation and descriptive coverage. **Potentially usable after evidence:** metric subsets with documented definitions, context, reset/aggregation behavior and healthy references. **Not established today:** a frozen symptom-eligible metric subset. All entries in the accompanying CSV are marked NOT_ESTABLISHED for symptom qualification, rather than falsely marked permanently unusable.

Dimensionless change scores might avoid unit conversion, but would still require comparable measurements, missingness/reset policy and a defensible normal distribution. They are not authorized merely because all units are UNKNOWN.

## 4. Sampling, missing values, duplicates and resets

The source profiler records headers, metric occurrence counts, timestamp scale/range/order, source-row conservation and selected-row counts. Its full-file output does not certify a per-component metric cadence, reset policy or missing-value semantics. A missingness counter is declared in `scan.py` but not used to produce full-series missingness qualification; absence of a reported problem is not zero missingness.

Earlier bounded E003 analysis reports prefix missingness and duplicate handling. Those prefix findings cannot be generalized to the entire later corpus. A repeated timestamp is not automatically a duplicate: distinct observations and metrics can share time. Projection row IDs preserve source-row identities, while duplicate span identities can prevent unique parent resolution. Full metric-series duplication/reset prevalence is not established by the retained summary metadata.

No zero-imputation, inferred sampling interval, reset correction or rate-of-change calculation was applied here.

## 5. Healthy/normal reference sufficiency

**A defensible healthy reference is NOT ESTABLISHED.** The context retention policy selects the union of annotation-centered [fault−300 seconds, fault+300 seconds] intervals. Inference projections use [fault−300 seconds, fault]. Source rows outside the retained union are counted/profiled but not retained in that context store. Full raw files may contain candidate normal periods; this assessment neither proves that they lack such periods nor certifies those periods as healthy.

Being before a fault annotation does not prove a component is normal: symptoms can precede annotations and overlapping incidents can contaminate references. A component not labelled as the root is not automatically healthy. Supplied annotations are points with unknown fault durations/recovery; “outside a listed point” is not a certified fault-free interval. No qualified repeated-workload or collection-stability reference was located in the inspected records.

Cross-component comparisons require comparable metric semantics and exposure. Counts depend on instrumentation, trace sampling and load; E004's count-reference performance does not establish normality or abnormality.

## 6. Leakage and oracle-time risks

| Risk | Existing boundary | Additional requirement before a qualification design |
|---|---|---|
| Root labels or fault reasons choose metrics/resources | Projection omits answer-bearing metadata | Independent eligibility must be frozen without label-conditioned feature selection |
| Supplied fault timestamp determines window | Present in orchestration and projection cutoff, even though no root enters ranking | Label the task retrospective; online triggers require an independent timeline |
| Future/post-fault observations in retained context | After segment is evaluator-only; operational projection stops at cutoff | Detector baseline/calibration cannot use later samples |
| Human-readable names carry cues | Projected identities are opaque hashes | Hashes retain identity equality and potential memorization; audit numerical/collection artifacts too |
| Ground-truth root presence filters cases | E004 retained all cases | Eligibility/abstention independent of root availability; retain accounting |
| Inspected 335 cases reused for confirmation | E004 all-case results have been inspected | Exploratory reuse is not an untouched holdout; an acceptable independence policy is missing |
| “Normal” baseline chosen after seeing rankings | No certified normal baseline presently supplied | Baseline acquisition/definition must precede outcome selection |
| Healthy controls inferred from absence | No such operational inference justified | Missing evidence remains unknown, not observed health |

Projection code guards against forbidden fields and future observations, but those engineering guards do not remove fault-conditioned sample selection or establish an independent evaluation split.

## 7. Retrospective evidence versus online detection

Retrospective question: given a specified evaluation window, is there a supported measurement pattern? Online question: does a policy detect that pattern on an independent stream without knowing a future fault time? Neither is answered by E003 replay or E004 structural ranking.

The available metadata can support a review of representation and observability. It cannot certify symptom detection quality, false alarms per normal exposure, onset delay or causal attribution. No inference of symptom labels was made from injected-root annotations.

## 8. Detection, symptom localization and RCA are separate

| Question | Required evidence | Current support |
|---|---|---|
| A: Is there abnormal behavior? | Supported metric semantics, defensible normal controls, independent abnormality validation | NOT ESTABLISHED |
| B: Which observed component carries a symptom? | Qualified policy and independent component symptom annotations or controlled observations | NOT ESTABLISHED |
| C: Which component is the faulty origin? | Frozen localization comparison and independent root evaluation | E004 supports only its restricted structural comparison, not symptom-supported RCA |

E003 before-only root availability is 284/335; 51 cases lack the labelled component in operational candidates. This is coverage and cannot be used to prove A or B, or to exclude difficult C cases. E004's Top-1/Top-3 result remains 3.08%/8.93% graph, 4.78%/14.93% counts and 1.80%/5.41% uniform, with all 335 windows retained. No new rankings were calculated.

## 9. Proposed research question and why no experiment design is supplied

Question retained for review: **Can a declared telemetry-only policy distinguish supported abnormal behavior from normal workload/collection variation in an observable component?** Component localization would be a separately evaluated downstream question.

There is not enough established evidence to choose a meaningful challenger/reference, baseline acquisition policy, split or acceptance criterion. A deviation threshold, persistent-change rule or neural method chosen now would be an assumption rather than a design supported by the inspected records. Therefore `symptom-evidence-qualification-proposal.md` is intentionally absent, as required for Outcome C by the attachment.

This assessment does not establish causality, operational RCA, online fault detection, safe remediation or production readiness. No symptom detector, E005 folder, registration, training split or result artifact was created.

## 10. Missing evidence and precise recommendation

Before a meaningful experiment proposal can be written, a human-reviewed evidence-acquisition scope should provide:

1. A bounded metric dictionary with source-supported units, kind, meaning, sampling, temporality/reset and aggregation behavior, plus exact component identity provenance.
2. Independently documented normal-control intervals with collection/workload context and known exposure; explicit contamination exclusions supported by evidence rather than guessed fault duration.
3. Independent validation of abnormal behavior, not only a faulty root label. Human annotation or a separately authorized controlled testbed could supply it, but neither is invented here.
4. An acceptable evaluation-independence plan. All 335 examined E004 cases must be marked reused/exploratory; fresh unseen data or a justified separately reviewed qualification policy is needed.
5. Evidence of where candidate records can actually be accessed and retained before any data operation. Current cloud/raw-data availability and backup integrity were not refreshed.

**Recommended next action:** review whether to authorize a bounded evidence-acquisition task for metric semantics and documented normal controls. First obtain supporting documentation; access additional retained/raw data only under explicit reviewed scope. No detector implementation or registration follows automatically.

## 11. Governance, fabrication checks and verification

E003's dated infrastructure-only approval is present. E004 and E002-R002 decisions remain proposals; no explicit approval provenance was supplied by this task. Historical checkpoint statements are preserved and explained by additive records. Both governance checkers passed before this inspection.

All inspected registry rows agree with corresponding retained profile metric occurrence counts. UNKNOWN records consistently have null evidence and zero asserted confidence. No fabricated metric semantic assertion or invented experiment result was identified in these inspected artifacts. This is not an exhaustive certification of every repository file. The previously reported frontend conflation of E001 test failures and a separate 47-pass engineering check remains a documented presentation issue; it was not silently rewritten.

The inventory tool checks the cited V006 metadata/profiles against the existing manifest, validates accounting and identities, and verifies its source hashes before/after. It reads JSON/source records only and refuses to overwrite dated outputs. No detector tests, new scientific evaluations or full raw-corpus audit were run.

Review record: `review-summary.json`. Inventory: `metric-eligibility-inventory.csv` and `inspection-summary.json`. Input/output identities: `inspection-source-hashes.json`.

```text
STATUS: NOT SUPPORTED
NEW EXPERIMENT REGISTERED: NO
EXPERIMENT EXECUTED: NO
RECOMMENDED NEXT ACTION: Review bounded acquisition of metric semantics and independently documented normal controls.
MAIN SCIENTIFIC RISK: Treating fault-conditioned or contaminated pre-fault data as normal evidence.
MAIN DATA LIMITATION: No qualified metric semantics or defensible healthy-reference policy established.
REVIEW REQUIRED: YES
NEXT HUMAN DECISION: Authorize or decline that bounded evidence-acquisition scope; do not authorize a detector on current assumptions.
```
