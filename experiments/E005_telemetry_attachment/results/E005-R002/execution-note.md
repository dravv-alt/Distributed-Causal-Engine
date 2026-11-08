# E005-R002 standalone local attempt

Date: 2026-11-07

## Execution

The frozen E005-R002 runner completed as a standalone local process because the OpenResearch (`orx`) CLI was not installed or available on PATH. Docker Desktop was reachable after an elevated read-only check, but this attempt used the repository's local Collector binary and receiver directly. It did not use OpenResearch or a committed immutable source snapshot.

The process environment cleared HTTP, HTTPS and ALL proxy variables and set `NO_PROXY` for loopback. The runner used synthetic fixtures and bound its Collector and receiver to `127.0.0.1`; no external requests or remote compute were used.

## Observed result

- Runner status: `PASS` for its implemented local checks.
- Three valid repetitions exported metrics, traces and logs successfully.
- Each malformed signal payload returned HTTP 400 without changing durable counts.
- Transient rejection recovered; the persisted counts were 8 trace payloads, 4 metric payloads and 4 log payloads.
- Persistent storage failure returned HTTP 503.
- Receiver restart preserved the durable record counts.
- All four SDK metric source points matched the durable sink on name, unit, value and `time_unix_nano`.

The detailed machine result and per-attempt logs are in this directory. The preflight records `orx_commit` as `UNAVAILABLE`.

## Interpretation limit

This is useful local evidence for the checks performed by the runner. It is **not** an OpenResearch-managed run, lacks an independently executed audit and does not establish full XP002 completion. It is not evidence about RCA accuracy or neuro-symbolic effectiveness. Preserve this limitation in any later review; do not alter the frozen protocol or historical E005-R001 records to describe this run as protocol-complete.
