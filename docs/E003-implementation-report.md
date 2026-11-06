# E003 implementation and adequacy report

Date: 2026-10-03. **Implementation exists; the downstream adequacy gate failed and awaits review.** E001 and E002 were not modified. No reasoning, anomaly detection, neural/causal models, planning, remediation, frontend or infrastructure was added.

## What OpenRCA actually contains

The downloaded snapshot contains Bank, two Market cloudbeds, and Telecom. It provides heterogeneous metric/trace CSVs, Bank/Market log CSVs, fault records, answer-bearing query scoring points, and a supplemental Telecom deployment spreadsheet. All original archive entries are inventoried and original ZIPs hashed. See [schema and mapping audit](openrca-dataset-analysis.md) and [manifest](../data/manifests/openrca.json).

335 nonblank fault records and 335 query records were counted across the four scenarios. This does not establish one-to-one fault/query correspondence. The ~63.94 GiB expanded archive volume was not fully decompressed or statistically profiled.

## What DCE can represent

The distinct `dce_foundation` package avoids collisions with the delivered R0 `dce` package. It supplies dataset-independent metric/log/span/entity/time/dependency/fault/ground-truth/incident values; explicit Decimal-based epoch normalization; strict source-profile parsing; immutable-source row provenance; and typed NetworkX operational/evaluation graphs.

Wide metrics expand into individual observations. Raw strings and every accepted source field survive in attributes. Unknown units, severity, duration semantics, entity kinds and end times remain null/UNKNOWN. CALLS edges require unique parent evidence in the same trace. Labels do not create operational entities, dependencies, diagnoses or causal claims.

The deterministic replay command supports new-directory serialization and a validation report. It can select any existing label-row incident ID, not just the eight experiment selections. Full-source-day scanning is supported syntactically but remains unverified at full scale; objects/graphs are materialized in memory.

## Cross-system experiment results

E003-R001 selected earliest/latest labelled scopes per scenario with a 2,000-row prefix limit per source telemetry file. Each scope was replayed independently twice; all canonical, graph and validation outputs matched. These are day scopes anchored by real fault records, not complete event-centered incident windows.

| Scope | Scanned rows | Mapped rows | Rejected | Observations | CALLS evidence edges | Exact roots observed |
|---|---:|---:|---:|---:|---:|---:|
| Bank@135 | 8,000 | 7,984 | 0 | 13,984 | 1,884 | 7/7 |
| Bank@134 | 8,000 | 5,989 | 2,000 | 11,956 | 0 | 10/10 |
| Market/cloudbed-1@30 | 16,000 | 16,000 | 0 | 22,000 | 384 | 15/22 |
| Market/cloudbed-1@68 | 16,000 | 16,000 | 0 | 22,000 | 361 | 11/23 |
| Market/cloudbed-2@2 | 16,000 | 16,000 | 0 | 22,000 | 377 | 16/22 |
| Market/cloudbed-2@75 | 16,000 | 16,000 | 0 | 22,000 | 397 | 18/26 |
| Telecom@2 | 10,381 | 10,381 | 0 | 11,524 | 0 | 6/6 |
| Telecom@52 | 10,382 | 10,382 | 0 | 11,528 | 0 | 4/4 |

Totals: **100,763 scanned = 98,736 mapped + 2,000 rejected + 27 outside-window**. Wide row expansion yielded **136,992 observations**: 103,008 metrics, 20,000 logs and 13,984 spans. There are 3,403 observed CALLS evidence edges, not necessarily 3,403 unique entity-pair dependencies. Source rows and canonical observations are intentionally different counts.

No exact duplicate source rows were found in these selected prefixes; fixture tests verify deterministic duplicate preservation. Source-order decreases were detected, notably 7,559 in Telecom@2, and sorted explicitly for replay. This describes source ordering, not measured live ingestion lateness.

Only four scopes had any root entity observation within five minutes of a labelled point; the count is at most one root per such scope. Prefix completeness cannot support event-level RCA. All reports mark downstream_ready false.

## Schema inconsistencies and failures

- **Bank timestamp profile:** same trace header, different epoch scale. March 25's 2,000 selected trace rows were rejected under the initial millisecond mapping. Follow-up first-row audit also identified seconds-scale values on March 23 and 24. The adapter was not silently revised after this result.
- **Bank boundary rows:** 27 rows across the two Bank scopes belong outside the declared source-local day and were counted separately rather than assigned invented times.
- **Bank parent conventions:** 93 self-parent spans in Bank@135, plus missing parents, need explicit semantics; no self-parent CALLS assertion was created.
- **Market:** missing parent/type fields and incomplete parent resolution; exact root identities present only partially in sampled telemetry. Coverage and aliases cannot be distinguished by this run alone.
- **Telecom:** no logs; all sampled spans have unresolved parents, and serviceName is missing in the initial trace profile. dsName remains a resource hint, not a verified graph relation.
- **Deployment topology:** workbook host relations are not represented operationally. V1's trace-derived topology is inadequate for deployment-level fault propagation reasoning.

Rejected records retain path, logical row, error and source fields. Unexpected headers fail loudly. The CLI exits nonzero on rejection/validation violations; UNKNOWN semantics appear as adequacy gaps even when parser schema checks pass.

## What information is lost or unusable?

For accepted records there is no intentional source-field dropping; original quoting/byte layout remains in the raw archive. Canonical float conversion can round, but exact strings survive in provenance. Missing fields remain explicit.

However, preservation is not understanding: metric units/temporality, duration/status semantics, typed deployment/resource relations, service aliases and query/incident associations are not usable as canonical structured evidence yet. Rejected Bank traces are absent from the operational graph. Parent gaps and bounded sampling remove usable topology/context. Fault end times are absent in the source and must not be invented.

## Assumptions

Explicit source timestamp profiles, UTC+08:00 label/day interpretation checked against all nonblank labels, opaque exact entity IDs scoped per scenario, parent→child as observed call direction, day scopes rather than fault intervals, and deterministic prefix selection. All units are UNKNOWN until supported; no LLM or incident-specific heuristics were used.

## Verification and provenance

39 pytest tests passed, including real archive samples from all four scenarios. Tests cover source-schema families, exact timestamps, invalid/missing values, identities, duplicates, ordering, parent direction, label isolation, preservation, multiple incidents, malformed input, bounded scans and repeated replay. The first sandbox fixture run failed on filesystem permissions; approved external execution resolved the test-environment problem, not a model defect.

CLI serialization was also verified against a real Bank sample, including separate label/operational outputs and refusal to overwrite existing artifacts. Rejected-row CLI behavior returns nonzero. Source/snapshot/result hashes were checked after execution; the executed model and adapter remain unchanged. `git diff --check` passed. A failed sandbox test scratch directory was retained and ignored rather than deleted.

[Run manifest](../experiments/E003_domain_model_adequacy/results/E003-R001/run-manifest.json) records code/test hashes, Git dirty state, versions, hardware identifiers, source snapshot hash and result hash. It does not imply a clean commit, hosted protocol freeze, measured peak RAM, full raw-file CRC test or production validation. No dependencies were installed; current Python 3.12/NetworkX 3.4.2/pytest 9.0.2 were used.

## Is the model adequate for downstream experiments?

**Not yet.** It is useful for representation inspection and preserving evidence, but not adequate for E006 symbolic RCA or other reasoning requiring units, reliable temporal relationships and complete typed topology. See [decision.md](../experiments/E003_domain_model_adequacy/decision.md) for the required revisions. Do not overwrite results or silently fix the model and declare the hypothesis accepted.

E001 remains baseline reproduction; E002 remains onset/timing analysis; E003 owns these adequacy findings. Proposed future tests include timestamp-profile validation, topology/identity reconciliation, and event-centered coverage, but no next experiment is registered or executed pending human review.
