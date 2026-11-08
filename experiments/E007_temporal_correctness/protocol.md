# E007 protocol v1 — event-time ordering, missingness, resets, and lateness

## Frozen synthetic input

Create 20 events at 100 ms intervals in `[0, 2 s)`, for one explicitly declared synthetic cumulative-counter series. Values increase from 0 through 9, then reset to 0 and increase through 9. Event `e005` has a timestamp but a missing value (`null`); do not impute. Add one event at exactly 2 s to test the exclusive end boundary. Use two 1 s event-time windows and a 100 ms allowed-lateness threshold. No random seed is needed because the input and schedules are fixed.

## Schedules and references

1. **Ordered control:** events in event-time order.
2. **Bounded disorder:** swap selected adjacent 100 ms events, so each inversion is at the configured bound.
3. **Beyond-bound late event:** deliver `e001`–`e019` first and `e000` last. The late event is expected to be quarantined; compare the output to the offline oracle on the exact accepted set.

The online accumulator uses an event-time watermark and explicit accepted/rejected ledgers. The independent offline oracle is separately implemented in the run script and recomputes windows, masks, counter deltas, and reset counts from the accepted records. For each identical accepted set, require exact field-by-field equality. For ordered versus bounded-disorder schedules, require identical accepted IDs and window features.

## Fixed policies

- Window interval is start-inclusive/end-exclusive.
- A missing value contributes to observation presence and missing count, but not the valid-value mask or counter arithmetic. No interpolation is permitted.
- For this synthetic counter only, the first valid value establishes a baseline. A monotone step contributes current minus previous. A decrease is one reset; its post-reset increment is the current value. Preserve raw event order provenance separately from event-time calculation.
- A record older than `max_seen_event_time - allowed_lateness` is rejected with an explicit reason. Equality to the watermark is accepted.
- Duplicate IDs are rejected. Invalid numeric values fail the run.

## Acceptance

- Ordered and bounded-disorder schedules accept all 20 in-window events and produce identical results.
- Online results exactly match the independent offline oracle for all three schedules on each schedule's accepted set.
- `e005` remains a missing value; its window reports one missing value without imputation.
- Exactly one counter reset is reported in the second window for the complete event set; no negative counter delta is produced.
- The event at exactly 2 s is rejected as out of window.
- The beyond-bound schedule rejects `e000` as late, records the reason, and the remaining accepted set matches the oracle.
- Any unmet criterion is reported as REVISE; no hidden repair or claimed system pass.

## Execution and provenance

Run locally with Python and no external services or network. Capture protocol/config/code hashes, Git HEAD and dirty status, Python/platform, exact command, immutable-in-run source snapshot, schedule results, independent comparison, and failures. This stage does not use OpenResearch because the `orx` CLI is unavailable on PATH.
