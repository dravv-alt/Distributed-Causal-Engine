# E007-R001 result interpretation

## Observed result

All eight preregistered assertions passed. The ordered control and bounded adjacent-reordering schedule each accepted the same 20 in-window events and produced identical window outputs. All three schedules matched the separately coded offline oracle exactly for their accepted event sets. The event at the exclusive 2-second endpoint was rejected as `out_of_window`. In the challenge schedule, `e000` arrived beyond the 100 ms bound and was rejected as `beyond_allowed_lateness`; the other 19 in-window events were retained. The missing value at `e005` remained missing, and one reset was recorded in the second window. Total synthetic counter delta was 18 under the protocol's explicit reset rule.

The machine-readable schedules and assertions are in `results.json`. `preflight.json`, `source-manifest.json`, and `source-snapshot.zip` record environment, hashes, and source contents. A separate artifact audit confirmed the run status, all assertions, snapshot hash, and inclusion of the new temporal module.

## Interpretation boundary

This establishes behavior only for a small deterministic Python prototype with one explicitly defined counter series, two fixed windows, and a 100 ms lateness bound. It does not prove the behavior of the DCE application at runtime: the module is not wired into an application ingestion or inference path. It does not validate units, arrival clocks, real telemetry, production throughput, neural inputs, RCA quality, or the optimality of the lateness/reset policy. Rejecting arrivals beyond the bound necessarily loses those records from that finalized view; any production use would need an explicit correction/retraction policy and operational review.

## Status

E007-R001: **synthetic technical checks passed; XP004 real-system qualification and independent human review remain pending**. OpenResearch was unavailable, so this was a local standalone run with no network access. No prior result or decision was modified.
