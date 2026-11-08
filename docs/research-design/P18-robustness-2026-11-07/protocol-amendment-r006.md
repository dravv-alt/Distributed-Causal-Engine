# P18-R006 amendment: package-level transactional temporal input

Date frozen: 2026-11-09. This is a prospective local engineering follow-up to P18-R005. Existing protocols, runs, decisions, and the original temporal module remain unchanged.

## Question

Does the additive package implementation `src/dce_foundation/representation_v2/temporal_transactional.py` preserve accumulator state when a counter value is invalid, allowing a corrected same-ID retry and a later in-window event?

## Design

Use the unchanged `EventTimeWindowAccumulator` as the comparison and the package-level `TransactionalEventTimeWindowAccumulator` as the candidate. For each of `NaN`, `Infinity`, `-1`, and nonnumeric text, create a fresh accumulator and:

1. Accept a valid event at time 2.
2. Submit an invalid event at time 15 and require `ValueError`.
3. Retry the same event ID/time with valid value `2` and require acceptance.
4. In a separate fresh accumulator, repeat steps 1–2, then submit a different valid event at time 3 with zero allowed lateness and require acceptance.

The unchanged implementation must reproduce the seen-ID poisoning after invalid input. The candidate must preserve accepted samples, rejected rows, seen IDs, and event-time watermark on the exception. Outputs and source hashes are written only under the new `results/P18-R006/` directory.

## Scope

This checks package-level behavior on deterministic local fixtures. It does not wire the candidate into the ingest path or claim real telemetry robustness, event-time correctness for unknown metric semantics, RCA quality, or production safety. No network or external services are used. No existing records or source files are edited.
