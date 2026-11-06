# E005 execution ledger

Protocol v1 is frozen in this new E005 record. No E005-R001 execution has been recorded yet.

Before launch, verify the OpenTelemetry Collector binary and hash, SDK/exporter versions, local-only endpoint configuration, database path, Python environment, hardware details where available, Git source snapshot, and result path. Use the fixed OpenResearch project command once configured. Commit only the reviewed E005 source/protocol needed for OpenResearch's immutable run snapshot; do not push.

Append the run record after each attempt. Preserve environment failures as failures. Never overwrite `results/E005-R001/` or interpret an incomplete direct-to-receiver diagnostic as full XP002 completion.

## E005-R001 — 2026-11-06

- Protocol: v1, local loopback only; synthetic fixtures only.
- Software: Python 3.12.3; OpenTelemetry API/SDK/exporter/proto 1.31.1; protobuf 7.36.2; Collector 0.164.0. Collector archive SHA-256: `ff9a3d79687cca7863bfbea1198542ca0c1800841289541913211d75ab6fea38`; executable SHA-256: `20aa55b613207c37f6b65df555b16001ec3f965d7218bf619742cb8579f0daa1`.
- Seven setup/implementation attempts were preserved. Attempts 1–5 ended before full protocol completion; attempt 6 was interrupted during the slow client retry for the persistent storage-failure case. Attempt 7 completed.
- Attempt 7 result: three valid metric/trace/log fixture repetitions; all SDK exports succeeded; malformed requests returned 400 for each signal and did not change durable counts; transient sink 503 recovered; persistent storage failure returned 503; receiver restart preserved record counts. Durable records: 8 trace payloads (8 spans), 4 metric payloads/points, 4 log records.
- Independent audit checked SQLite integrity, payload hashes, all signal counts, resource identity, metric name/unit/value and timestamp presence, trace root/child IDs, log fields, malformed rejection, storage failure status, and restart counts. It found no mismatch in those checks.
- Limitation: the SDK-generated metric timestamp was present in the stored request but was not captured independently before export, so exact source-to-sink equality for that timestamp is **UNKNOWN**. The preregistered exact timestamp fidelity criterion is therefore not fully verified.
- Worktree was dirty before this run; current source files were hashed in `results/preflight-E005-R001-A007.json`. CPU/RAM were not obtained. Results are local and synthetic.
- Proposal: **REVISE / bounded ingestion behavior works; metric timestamp fidelity still needs direct source-to-sink verification**. This is not an RCA accuracy or neuro-symbolic effectiveness result. Human review required.

See [E005-R001 review proposal](results/E005-R001/review-proposal.md), per-attempt logs and [independent audit](results/E005-R001/attempt-007/independent-audit-002.json).
