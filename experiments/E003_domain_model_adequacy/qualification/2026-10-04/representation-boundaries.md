# What this qualification does and does not establish

## The two outputs

1. **Audit/evaluator record:** exact source fields, file/row provenance, labels, scoring points, raw identities, rejected-row pointers and incident coverage. This is not model input.
2. **Inference projection:** opaque deterministic identities, finite metric values, observed timestamps, raw span duration with UNKNOWN unit, and trace edges supported by two spans inside the declared window. It excludes raw log text, paths, names, fault metadata and scoring points.

The compressed context database retains exact selected CSV field strings, including unrecognized columns. It is not a substitute for the complete raw corpus: rows outside all incident windows are counted and profiled, not retained in this database. Full source files remain untouched.

## Time and selection

The census reads every CSV to EOF. Each completed file has a decompressed byte hash and ZIP CRC verification. Four timestamp scales are tested against the source-local UTC+08 day with a fixed one-hour profiling allowance. The strict-day count is separate from that allowance. Out-of-day and malformed rows remain visible; no clock correction or incident-specific conversion is applied.

Incident retrieval uses the union of all fixed five-minute-before/five-minute-after windows. Root identities are not provided to the scanner. A retrospective after segment is used only to assess coverage. The inference projection stops at the annotation point, and its window is a declared representation test input, **not a claim that a deployed agent knows fault onset**. Official query windows require a separately qualified evaluation setup.

## Identity, graph and unresolved data

Original v2 canonical types, identity evidence and workbook relationships remain in AM001. This amendment does not revise those historical outputs. Operational trace edges are reconstructed from spans in each permitted window. Missing, duplicate, self-referential or otherwise unsupported parents remain explicit states. A parent outside the permitted window is not imported merely to complete a graph.

Workbook relations have UNKNOWN temporal validity and are excluded from these time-qualified projections. An exact root identifier appearing in telemetry is resource evidence, not proof of a service alias or causal connection. UNKNOWN identity kinds are not inferred from naming conventions.

## Metric qualification

The registry inventories source metric names and counts, including wide-table value fields. UNKNOWN unit, temporality, aggregation and kind are acceptable under the newly authorized AM002 criterion. They prohibit transformations that require those semantics. This is a changed, prospectively frozen acceptance criterion; it does not convert AM001's historical PARTIAL result into a PASS.

## Evaluation and leakage limits

Query/label association requires independent, unique source-supported matching. Equal counts and row order are not evidence. Unresolved matches remain UNKNOWN. Labels are used after telemetry retrieval to measure root coverage, never to select resources or build inference evidence. Hashing an identity removes readable name cues; it does not prove the numerical signals are free of benchmark artifacts. No learned model or RCA accuracy test runs here.

## Repeatability and readiness

Two independently constructed projections are compared for all annotation windows. This tests deterministic projection from retained context; it is not two full scans of the complete corpus. A completed source profile may be inherited only with its profile hash, byte hash, EOF/CRC evidence and conserved selected-row count.

The mechanical representation gate, official-scoring readiness, observable-root coverage and human approval are separate decisions. A representation PASS cannot authorize raw-data deletion, prove RCA quality, or silently qualify cases whose roots or query associations are missing. E003 stops for review.
