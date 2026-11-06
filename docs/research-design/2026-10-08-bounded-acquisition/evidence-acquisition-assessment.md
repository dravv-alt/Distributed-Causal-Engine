# Bounded evidence acquisition: stop report

Date: 8 October 2026. Authority: the user's explicit documentation plus retained-telemetry inspection authorization. This is descriptive acquisition, not an experiment, detector evaluation or gate approval.

## Answers to the three stopping questions

| Question | Answer within this scope | Evidence and remaining requirement |
|---|---|---|
| Is a sufficiently supported metric subset established? | NOT ESTABLISHED | Source schemas and some timestamp descriptions are available, but local units, measurement meanings, temporality, aggregation and reset behavior remain unsupported. Name resemblance does not qualify a local metric. |
| Is a defensible normal-control source established? | NOT ESTABLISHED | The available context is inherited fault-centered retained telemetry. Numerical variation is observed, but no sampled population has independently supported healthy status. |
| Is an independent evaluation split potentially available? | NOT ESTABLISHED | This sample comes from already used retained context. No untouched exposure population with supported semantics and normal controls was identified. This does not prove that an independent population cannot be obtained elsewhere. |

Acquisition stops here. No further payload inspection, detector work, successor registration or execution is authorized by this report.

## What was actually inspected

The [fixed scope](acquisition-scope.md) and [sample plan](sample-plan.json) preceded payload access. Selection used scenario, source path, date and metric names, without values or fault labels. Two source files per scenario, their first retained block and up to three preselected names per file were used. Each block was decoded within explicit bounds and only its first 256 rows inspected. No raw dataset was accessed.

The [retained sample summary](retained-sample-summary.json) records **8 blocks, 7,245 decoded rows, 1,869 inspected rows and 56 component/metric series**. Compressed payloads total **78,030 bytes**. **27 of the 56 series had more than one distinct finite numeric value**. These are exact descriptive sample counts; they do not measure healthy variation, symptoms, accuracy or detection performance.

| Scenario and source | Selected names observed in prefix | Series summarized |
|---|---|---:|
| Bank, 2021_03_04, metric_app.csv | cnt, mrt, rr | 33 |
| Bank, 2021_03_04, metric_container.csv | None of the three preselected names | 0 |
| Market/cloudbed-1, 2022_03_20, metric_container.csv | None of the three preselected names | 0 |
| Market/cloudbed-1, 2022_03_20, metric_mesh.csv | None of the three preselected names | 0 |
| Market/cloudbed-2, 2022_03_20, metric_container.csv | None of the three preselected names | 0 |
| Market/cloudbed-2, 2022_03_20, metric_mesh.csv | None of the three preselected names | 0 |
| Telecom, 2020_04_11, metric_app.csv | avg_time, num, succee_num | 3 |
| Telecom, 2020_04_11, metric_container.csv | container_cpu_used, container_fgc, container_fgct | 20 |

Five prefixes did not contain their preselected names. No replacement was made. This is a prefix limitation, not evidence that those metrics are absent from their full source files. Observed timestamp gaps are reported as spacings, not sampling schedules or proof of missing records. Selected numeric observations were parseable; that does not qualify the remaining population or establish units.

## Authoritative documentation and conflicts

The [reference archive](official-reference.json) preserves six official Microsoft/OpenRCA files at commit `c1bd4af7f635171a1c31cdd567c07d698dff6abc`, with URLs, byte hashes, retrieval time and MIT license. Total downloaded content is 31,311 bytes. **The match between this upstream code revision and the local dataset version is UNKNOWN.** External examples and heuristic instructions are source-authored material, not DCE measured findings.

- The Bank schema lists rr, sr, cnt and mrt but does not establish their expansions, units, aggregation or counter semantics. Its blanket statement that trace timestamps are milliseconds conflicts with inherited local profiles: seven Bank trace sources select milliseconds, while `2021_03_23`, `2021_03_24` and `2021_03_25/trace/trace_span.csv` select seconds. This acquisition did not rerun timestamp qualification. Neither description was silently reconciled and no records were changed. See the [official Bank source](https://raw.githubusercontent.com/microsoft/OpenRCA/c1bd4af7f635171a1c31cdd567c07d698dff6abc/rca/baseline/rca_agent/prompt/basic_prompt_Bank.py).
- The Telecom source describes milliseconds for metric/trace timestamps and lists app fields, but does not establish the unit of avg_time or counter/reset semantics of num and succee_num. Its clarification includes startTime among five KPIs although startTime is the timestamp field: it is not qualified here as a measured symptom feature. See the [official Telecom source](https://raw.githubusercontent.com/microsoft/OpenRCA/c1bd4af7f635171a1c31cdd567c07d698dff6abc/rca/baseline/rca_agent/prompt/basic_prompt_Telecom.py).
- The Market schema supplies component granularity and timestamp descriptions. It does not prove local aliases, exporter versions or meanings of the sampled container/mesh names. These descriptions are documentation leads, not completed local qualification.
- The [official cAdvisor metric table](https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md) defines `container_cpu_cfs_periods_total`, `container_cpu_cfs_throttled_periods_total` and `container_cpu_cfs_throttled_seconds_total` as counters, with seconds for the last. Selected local Market names omit `_total`. Without export configuration or transformation provenance, this resemblance cannot transfer those definitions to the local registry.
- The OpenRCA README refers to fixed sampling frequency without a numeric per-series schedule. Sparse retained windows do not independently establish that schedule. The upstream agent prompt's full-file percentiles and threshold-relaxation workflow are heuristic instructions, not a validated healthy-control design. They were not implemented or adopted.

No illustrative latency/error-rate values were entered as measured findings. No metric was promoted from UNKNOWN. No fabricated local finding was identified in the inspected material; the documentary inconsistencies above are reported rather than repaired. This was not an exhaustive repository fabrication audit.

## Why variation is insufficient

Existing retention selects unions of fault-centered windows; rows outside them are counted but generally not retained in this store. Pre-fault timestamps, low values, unlabeled components and missing logs do not establish health. The sample selection is independent of labels within a previously label-conditioned population. Repeated observations from these same windows are not independent controls or a new untouched holdout.

## Preservation and permitted next action

Existing experiment decisions remain unchanged. Separate amendments record the user's E004 execution acceptance with REVISE/structural-prior-only retained, and the separate E002-R002 REVISE approval. Neither grants a successor.

The sampler used read-only immutable SQLite access and checked sampled payload hashes, source-profile hashes and database size/mtime. It did **not** reverify the historical full database checksum: doing so would exceed this bounded acquisition. Verification results are recorded separately in `verification.json`.

The next useful review decision is whether to authorize obtaining source-owner metric dictionaries/exporter configurations, a documented healthy-control population and a genuinely separate exposure population. Those are missing prerequisites, not a proposed detector or registered experiment. Existing records must remain preserved. E005 registration and execution remain unauthorized.
