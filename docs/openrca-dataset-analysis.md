# OpenRCA dataset analysis — E003

Inspection date: 2026-10-03. Evidence: [local manifest](../data/manifests/openrca.json), source ZIP headers and bounded CSV profiles, not documentation-only assumptions. All originals remain unchanged in `data/dataset`. Source release/commit: **UNKNOWN**. Download completeness against upstream: **unverified**.

## 1. Actual source layout

```text
data/dataset/
  Bank.zip                           # 53 files; 24.59 GiB expanded
    Bank/{query.csv,record.csv}
    Bank/telemetry/{date}/{metric,log,trace}/*.csv
  Market.zip                         # 41 files; 22.90 GiB expanded
    Market/cloudbed-{1,2}/{query.csv,record.csv}
    Market/cloudbed-{1,2}/telemetry/{date}/{metric,log,trace}/*.csv
  Telecom.zip                        # 108 files; 16.45 GiB expanded
    Telecom/{query.csv,record.csv}
    Telecom/telemetry/{date}/{metric,trace}/*.csv
  OpenRCA-20261002T162203Z-1-004.zip
    OpenRCA/AppTelecomDeploymentList.xlsx
  OpenRCA-20261002T162203Z-1-004/      # previously extracted workbook; not rewritten
```

Bank dates: 2021_03_04, 05, 06, 07, 09, 10, 12, 23, 24, 25. Market: 2022_03_20 and 21 in both cloudbeds. Telecom: 2020_04_11, 20, 21, 22, 23; 2020_05_22 through 31. No Telecom log CSV is present. Absence is not proof the underlying system produced no logs.

Main telemetry/label ZIPs contain 202 files and approximately 63.94 GiB expanded. No extraction is needed: adapters stream ZIP entries. Each file's compressed/uncompressed size, CRC and headers are inventoried. SHA-256 hashes cover original archives. Full decompression/CRC integrity testing and full population row counts have **not** been performed.

## 2. Exact discovered CSV schemas

Each telemetry header in every date was inspected; no unexpected headers were found. These are CSV strings at the source boundary; conversion types are defined below.

| System | Filename | Exact ordered header |
|---|---|---|
| Bank | metric_container.csv | timestamp, cmdb_id, kpi_name, value |
| Bank | metric_app.csv | timestamp, rr, sr, cnt, mrt, tc |
| Bank | log_service.csv | log_id, timestamp, cmdb_id, log_name, value |
| Bank | trace_span.csv | timestamp, cmdb_id, parent_id, span_id, trace_id, duration |
| Market | metric_service.csv | service, timestamp, rr, sr, mrt, count |
| Market | metric_container.csv | timestamp, cmdb_id, kpi_name, value |
| Market | metric_node.csv | timestamp, cmdb_id, kpi_name, value |
| Market | metric_runtime.csv | timestamp, cmdb_id, kpi_name, value |
| Market | metric_mesh.csv | timestamp, cmdb_id, kpi_name, value |
| Market | log_proxy.csv | log_id, timestamp, cmdb_id, log_name, value |
| Market | log_service.csv | log_id, timestamp, cmdb_id, log_name, value |
| Market | trace_span.csv | timestamp, cmdb_id, span_id, trace_id, duration, type, status_code, operation_name, parent_span |
| Telecom | metric_app.csv | serviceName, startTime, avg_time, num, succee_num, succee_rate |
| Telecom | metric_container.csv | itemid, name, bomc_id, timestamp, value, cmdb_id |
| Telecom | metric_middleware.csv | itemid, name, bomc_id, timestamp, value, cmdb_id |
| Telecom | metric_node.csv | itemid, name, bomc_id, timestamp, value, cmdb_id |
| Telecom | metric_service.csv | itemid, name, bomc_id, timestamp, value, cmdb_id |
| Telecom | trace_span.csv | callType, startTime, elapsedTime, success, traceId, id, pid, cmdb_id, dsName, serviceName |
| Bank | record.csv | level, component, timestamp, datetime, reason |
| Market | record.csv | timestamp, level, component, reason, datetime |
| Telecom | record.csv | level, reason, component, timestamp, datetime |
| All | query.csv | task_index, instruction, scoring_points |

There are 24 distinct system/filename/header groups: 18 telemetry and 6 label/query groups. Market groups aggregate the two cloudbeds, but identities remain separate.

## 3. Field-by-field canonical mapping

All accepted source fields survive exactly in `Provenance.attributes`, together with ZIP-entry path and logical CSV row number. Source row numbers count CSV records, not physical lines inside multiline messages. Raw numerics remain strings there even when canonical values use floats. No source payload is claimed semantically understood merely because it was retained.

| Source fields | Canonical mapping | Interpretation / caveat |
|---|---|---|
| timestamp / startTime | EventTime.source_value, source_field, source_unit; exact epoch_ns and UTC string | Explicit schema profile chooses epoch scale; never uses ingestion time |
| cmdb_id / tc / service / serviceName (app metrics) | Entity.source_id and environment-scoped hashed ID | Opaque identity; service vs pod vs node kind UNKNOWN |
| kpi_name / name | MetricObservation.name | Source names retained, no cross-system metric alias |
| value (metrics) | finite float or None | Blank = explicit missing; NaN/Inf/malformed rejected; raw string preserved |
| rr, sr, cnt, mrt, count | separate named MetricObservations | Bank/Market wide rows expand; acronym meanings, temporality and units UNKNOWN |
| avg_time, num, succee_num, succee_rate | separate named MetricObservations | Telecom wide rows expand; no assumed ratio/percent conversion |
| itemid, bomc_id | source attributes | Catalogue semantics UNKNOWN; not discarded |
| log_id, log_name | source attributes | Source IDs retained separately from deterministic canonical row ID |
| value (logs) | LogEvent.message, or None if blank | No parsing of severity/status from free text |
| trace_id / traceId | TraceSpan.trace_id | Exact source string, scoped by environment |
| span_id / id | TraceSpan.span_id | Exact source string; duplicate identity is ambiguous, not merged |
| parent_id / parent_span / pid | TraceSpan.parent_span_id | Empty = absent; nonempty unresolved sentinels are reported, not guessed |
| duration / elapsedTime | TraceSpan.duration_raw | Numeric validity checked; unit UNKNOWN; end time remains None |
| status_code / success | TraceSpan.status + original attributes | Raw token, canonical success/error semantics UNKNOWN |
| type, operation_name, callType | source attributes | Preserved; no automatic resource or protocol type inference |
| dsName, serviceName (traces) | source attributes | Resource/service hints preserved; do not assume dsName is a verified dependency endpoint |
| level (labels) | FaultEvent source attributes | Label scope; does not silently type operational entities |
| component | FaultEvent.entity_id + source attributes | Same exact identity function as telemetry; unresolved aliases reported |
| reason | FaultEvent.reason | Label text, not an inferred diagnosis or standardized fault ontology |
| datetime | label source attributes + epoch consistency audit | UTC+08:00 interpretation checked against epoch |
| task_index, instruction, scoring_points | GroundTruth.queries | Evaluation-only; includes answer-bearing scoring_points, not inference input |

Source-field byte-level reconstruction is not promised: CSV quoting/order/line endings survive in the immutable archives, not canonical objects. Floating numeric conversion may round, but exact source value is retained. Unknown fields cause strict schema failure rather than silent loss.

## 4. Event-time semantics

Observed magnitude/date alignment supports the following scales, with a critical within-Bank variation discovered by E003-R001. The v1 adapter uses the initial millisecond Bank trace profile and therefore deliberately reports rejections for the later seconds-scaled files; it has NOT been silently patched after the run.

| Profile | Epoch scale |
|---|---|
| Bank/Market metrics and logs | seconds |
| Bank traces, March 4–12 observed dates | milliseconds |
| Bank traces, March 23–25 | seconds in inspected first rows; v1 adapter rejects these as unsupported profile |
| Market traces | milliseconds |
| Telecom metrics and traces | milliseconds |
| All record.csv label timestamps | seconds |

Event time is integer nanoseconds derived with Decimal, not floating epoch arithmetic. Source fractional precision is retained. Clock accuracy and collection latency are UNKNOWN. No receipt/processing timestamp is fabricated for offline records.

All 335 nonblank fault rows have matching epoch and datetime under UTC+08:00. Source-local directory dates select a UTC+08:00 day with half-open boundaries converted to UTC. Directory date is not assumed to be UTC. Inference/test splits and watermarking are out of scope.

Replay sorts by `(epoch_ns, source_path, source_row, canonical_id)`. Out-of-order rows are counted before sorting. Duplicate rows are retained with row-specific IDs and explicit quality flags. Equal timestamps are not automatically duplicates. Missing/invalid required times are rejected with source-row evidence; no interpolation or imputation occurs.

Observed positive successive metric deltas are reported per file after grouping by entity/metric. Out-of-order transitions do not determine cadence. These deltas are **not** a certified sampling interval, especially under prefix sampling or entity-major file order.

## 5. Identity and topology

Canonical entity IDs hash `[scenario, exact_source_identity]`; Bank A and Telecom A cannot collide. Case, punctuation and original IDs survive. Leading/trailing identity whitespace is rejected, not silently trimmed. No pod-to-service consolidation, host parsing or service alias mapping is attempted.

Graph: NetworkX MultiDiGraph. Incident, entity, observation, trace and dependency-evidence nodes have explicit roles. HAS_OBSERVATION, OBSERVED_ON, IN_TRACE, PARENT_SPAN and SUPPORTED_BY preserve evidence relationships. CALLS is observed structural evidence from a unique parent in the same trace, directed parent entity → child entity. Cross-trace joins and ambiguous parents do not produce CALLS edges. This is an operational assumption about parent-span semantics, not proof of complete topology or causality. Self-parent spans are reported; service self-calls and cycles are allowed.

No generic RELATED_TO or causal edges are produced. Possible/established causal relations are future epistemic categories, not claims in this graph. No hypotheses are fabricated in a representation experiment. No temporal PRECEDES edge is guessed from source row order. Bank@135 includes 93 self-parent spans: those references are reported and do not produce CALLS edges. Empty parents and self-parent root conventions need explicit source semantics, not blanket invalidation.

Deployment workbook: Sheet1 contains 201 XML row elements, including formatting-only rows. Columns A–E are Type, Number, Host, Name, From (containers). Explicit Host/Name pairs include redis_001 → os_003 and docker_001 → os_017. `From (containers)` includes container_001/container_002 aliases. These are preserved in the external workbook but **not mapped by adapter v1**. RUNS_ON support, blank/merged-cell rules and alias evidence need review. This is an adequacy gap; trace CALLS cannot substitute for deployment topology.

Market metric identifiers sometimes contain node/pod encodings; no RUNS_ON is inferred from punctuation alone. Telecom dsName resource hints also remain unmapped structured relations. The current graph is a typed partial evidence graph, not a complete distributed-system model.

## 6. Labels and incident semantics

Nonblank CSV counts: Bank 136 records / 136 queries; Market/cloudbed-1 70 / 70; Market/cloudbed-2 78 / 78; Telecom 51 / 51. A previous csv.reader inspection counted a blank Telecom record row as an extra row; DictReader's 51 nonblank records is the corrected count. Matching counts do not establish row-wise correspondence.

Incident ID is `<scenario>@<record.csv logical line>`. A selected label anchors a day scope; all labels within that day become point FaultEvents in GroundTruth, not invented-duration faults. Additional task queries remain evaluation metadata for the scenario; no unsupported query-to-incident join is asserted.

The operational graph and `operational_dict()` exclude ground truth. The separate evaluation graph represents CONTAINS and labelled AFFECTS. An absent label entity becomes an evaluation-only reference, not a falsely observed operational node. `ground_truth_roots_observed` reports exact identity coverage only; it does not validate an RCA prediction.

## 7. Profiling evidence and limitations

The manifest profiles the first 256 telemetry rows of every CSV and all labels. This is not a full-data statistical audit. Per-field cardinality is the maximum distinct count within one profiled file, not global cardinality. Full counts, duplicate prevalence, missingness rates and cadence remain UNKNOWN outside inspected prefixes.

Observed prefix missingness: Market service-log value (2), Market parent_span (57), Market trace type (48), Telecom bomc_id (2), Telecom trace serviceName (3,840). No exact duplicate source rows or CSV field-count errors were found in these initial profiles. E003's larger selected prefixes may find additional failures; see results rather than extrapolating this profile.

Unresolved semantics: metric units and temporality; acronym mappings; span duration units; raw success/status-code meanings; empty vs nonempty root markers; service/pod/node aliases; label-to-query correspondence; fault end times; complete deployment/call topology; raw telemetry licence/version provenance. No service latency, error rate or RCA feature vector is fabricated from these unknowns.

## 8. Reproduction and deterministic behavior

From repo root, using the existing environment:

```powershell
$env:PYTHONPATH = 'src'
python -m dce_foundation.replay.openrca --incident Bank@2 --max-rows-per-file 2000
```

Omit `--max-rows-per-file` for a full streaming source-day scan, subject to memory required for materialized objects and NetworkX. This path has not been stress-tested at full scale. `--output data/processed/openrca/<new-run>` writes separate operational, label, graph and validation files; it refuses to overwrite an existing output directory. Serialized operational outputs still contain raw telemetry and require access controls.

Run `python -m dce_foundation.evaluation --inspect` only for a new manifest location/version: the current manifest is exclusive-create, not silently overwritten. The experiment harness also refuses existing run directories. Results include canonical/graph digests and a second independent replay comparison. These verify the represented prefix, not upstream dataset integrity or downstream RCA quality.

## 9. Adequacy gate

Preserving source fields prevents silent payload loss; it does not make UNKNOWN fields usable to reasoning. E003 must expose unresolved topology, identities, time units, semantic fields and event coverage. Refer to the [decision gate](../experiments/E003_domain_model_adequacy/decision.md). No downstream reasoning or next experiment is authorized by parser success.
