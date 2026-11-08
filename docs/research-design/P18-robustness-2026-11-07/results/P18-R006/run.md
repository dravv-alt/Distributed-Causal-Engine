# P18-R006 run record

Date: 2026-11-09. Local deterministic execution of the frozen [R006 protocol](../../protocol-amendment-r006.md).

The unchanged comparison reproduced the invalid-event-ID poisoning for all four values (`NaN`, `Infinity`, `-1`, and nonnumeric text): validation raised after adding the event ID, so a corrected same-ID retry was rejected. The package candidate raised the same validation errors without changing accepted samples, rejected records, seen IDs, or watermark; all four corrected retries were accepted. Candidate lower-timestamp probes were accepted after the invalid attempts.

All four runner assertions passed. The read-only independent output/provenance audit passed all eight checks, including five source hashes. Network and external services were not used. Two runner failures and one audit-script failure are retained as `attempt-001-runner-failure.json`, `attempt-002-runner-failure.json`, and `audit-attempt-001-failure.json`; none changed the original E007/R005 artifacts.

The result qualifies only this package-level deterministic input contract. The ingest path does not yet use the candidate; real telemetry, end-to-end robustness, and RCA effectiveness remain unestablished.
