# E006-R001 result interpretation

## Observed

- All nine configured blind audit files were present, matched the pinned dataset revision, and declared that labels were not loaded.
- There were **560 distinct metric feature names** across the nine cases and **zero names common to all nine**.
- Per-case metric feature counts ranged from **58 to 345**; sampled metric rows ranged from **63 to 1,801**.
- Metric missing cells ranged from **0 to 37,382**.
- Logs were available in **6/9** sampled cases; traces were available in **4/9**.
- For sampled cases with logs, the prior field audits report zero log timestamps absent from the metric timestamp set. Metric timestamps absent from the log timestamp set ranged from **1 to 506** where logs were present.
- A separate aggregation command independently recomputed the 560-name union and empty intersection from the input catalogs; it passed.

Per-case fields, row counts, missingness, overlap counts, and source hashes are in `feature-coverage.json` and `source-manifest.json`.

## Interpretation boundary

This is a deliberately selected nine-case sample, not a random or complete dataset scan. The differing names show that a single fixed metric schema cannot be assumed for these samples. They do not establish population-wide coverage or prove that a union-based model would be useful. Exact timestamp equality does not verify units, timezone, sampling cadence, event-time semantics, or aligned evaluation windows. Metric units, temporality, aggregation, kind, and reset behavior remain `UNKNOWN`. No DCE feature extractor or RCA method was evaluated, and no root-cause labels were read.

## Execution and review status

The run was standalone and local because `orx` was unavailable on PATH. No network access was used by the runner. Independent recomputation covered the feature union/intersection and label-blind declarations; it is a script-level check, not independent human review. E006-R001 is therefore a completed descriptive audit with review pending, not an XP003 pass or evidence of RCA effectiveness.
