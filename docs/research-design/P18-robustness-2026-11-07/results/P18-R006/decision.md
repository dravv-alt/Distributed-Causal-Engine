# P18-R006 scoped decision proposal

**Technical outcome:** the package-level candidate passed the frozen invalid-input transactionality checks. The unchanged implementation reproduced seen-ID poisoning for all four invalid values; the candidate preserved its state, accepted corrected retries, and preserved its watermark. The independent output/provenance audit passed.

**Scope limit:** the candidate is not wired into the telemetry ingest path. This does not close P18, qualify XP004 on real telemetry, or demonstrate end-to-end robustness or RCA quality. Human review remains pending.

The next useful engineering step is an explicitly reviewed integration into the ingest path, followed by a new local run against that path. Existing E007 and P18-R005 records remain unchanged.
