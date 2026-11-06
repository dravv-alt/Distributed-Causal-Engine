# E005-R002 follow-up protocol — exact metric timestamp fidelity

**Status:** Frozen for E005-R002 before execution.  
**Execution boundary:** Local loopback only; synthetic telemetry only; no remote compute, external dataset, literature retrieval, or telemetry upload.

This follow-up repeats the E005-R001 acceptance cases and resolves one missing measurement: capture each metric point's SDK timestamp immediately before OTLP serialization and compare it exactly with the durable receiver record. The research question and acceptance criteria are unchanged.

## Question and hypothesis

Test whether an instrumented local workload can send known metrics, traces and logs through the configured OTLP/HTTP path into DCE while preserving their declared fields, rejecting malformed input, and acknowledging only durable writes. The hypothesis and boundaries are in [hypothesis.md](hypothesis.md).

## System under test and reference

The system under test is the new E005 DCE receiver and local durable store. The reference is the exact set of deterministic signal fixtures produced by the instrumented workload before export. The fixture manifest is evaluator-owned and unavailable to the receiver as labels or scoring information. No OpenRCA or R0 telemetry is used.

The execution path must include an OpenTelemetry SDK, an OpenTelemetry Collector configured only for loopback, OTLP/HTTP export, the DCE receiver, and local durable storage. If a real Collector cannot be started, record an environment failure and stop the full XP002 gate; a direct SDK-to-receiver diagnostic may be retained only as an explicitly incomplete subtest.

## Controlled cases

1. **Valid delivery:** one deterministic metric, one trace with a parent/child pair, and one structured log. Use explicit resource attributes, metric unit, timestamps, span IDs and log severity/body. Repeat each fixture three times from a fresh local store.
2. **Malformed input:** send one invalid protobuf body to each signal endpoint. The receiver must return a client error and persist no records from that request.
3. **Transient rejection and retry:** configure the local receiver to return HTTP 503 before writing the first valid request, then accept the retry. The SDK/Collector export path must eventually report success and retain the expected logical telemetry. Duplicate delivery behavior is counted and reported; this protocol makes no exactly-once claim.
4. **Durability:** stop and restart the receiver after acknowledged valid delivery, then verify the same logical records remain available from the local store.
5. **Storage failure:** inject a local write failure before commit. The receiver must not return success for that request and must not report the record as durably present.

No other variable changes between cases. Use fixed fixture IDs, timestamps, resource attributes and configuration. Record each request/response and test attempt without storing secrets or raw host telemetry. The metric exporter records metric name, unit, value and `time_unix_nano` from the SDK object before calling the OTLP exporter. Compare sorted source and sink tuples exactly.

## Measures and acceptance criteria

- **Field fidelity:** 100% exact match for the preregistered fields in all acknowledged fixtures: signal type, resource attributes, metric name/unit/value/timestamp, trace/span/parent IDs and timestamps, and log body/severity/timestamp.
- **Malformed rejection:** all three malformed signal requests receive a 4xx response and create zero durable records.
- **Acknowledgment safety:** every 2xx response corresponds to a committed durable record; injected storage failure must not receive 2xx.
- **Transient retry:** the valid request rejected before storage is eventually retained after retry. Report attempts and duplicate count; duplicates are not silently discarded or interpreted as exactly-once semantics.
- **Restart durability:** all acknowledged expected records remain after the receiver process restarts.
- **Coverage:** every planned fixture and case is accounted for; no skipped case is counted as passing.

These are correctness invariants for this ingestion contract, not RCA-quality thresholds. No timing or throughput threshold is claimed.

## Leakage and blinding

The receiver sees operational telemetry only. Fixture expectations are held by the independent verifier and opened after responses and persisted records are captured. Fault-case labels are never embedded in telemetry or exposed to the receiver. There is no model fitting or tuning.

## Provenance and repeatability

Before execution record the source snapshot/hash, Python and OpenTelemetry versions, Collector version/hash, OS/CPU/RAM where queryable, resolved configuration, database settings, and exact command. Use no randomness; fixture IDs and timestamps are deterministic. Save logs, request/result digests, database integrity evidence, source metric tuples and exact source/sink comparison under a unique E005-R002 result directory. Never overwrite an existing result.

## Decision rule

Technical PASS requires every acceptance criterion above, every case accounted for, independent verification, and no unexplained duplicate, loss, acknowledgment, or provenance issue. Any unmet criterion is REVISE or environment-blocked as appropriate. Technical PASS establishes ingestion correctness only and does not prove RCA effectiveness. This run uses OpenResearch's local backend and a committed source snapshot; it does not compare RCA methods.

## Limitations

One local environment and a small deterministic fixture set do not establish production availability, security, load capacity, telemetry coverage for real services, detector quality, neuro-symbolic benefit, or root-cause accuracy.
