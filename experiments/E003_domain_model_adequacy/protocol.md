# Protocol v1 (2026-10-03)

Inspect headers of every CSV entry before implementing source mappings. Preserve originals in place; use a reference manifest rather than copying 8+ GiB archives. Hash each archive; retain ZIP entry sizes and CRC metadata (CRC is not cryptographic integrity).

Select the earliest and latest timestamped record in each of the four scenarios, breaking ties by source row. Define an explicit source-local UTC+08:00 day window containing that labelled event and convert its boundaries to UTC. Load all modalities available on that date. Labels describe point events: do not invent incident duration. A day window is a representation scope, not fault duration. Include all labels in the day; do not assume query rows correspond one-to-one to fault records.

The initial resource-bounded adequacy run scans the first 2,000 rows per selected telemetry file. This is a prefix, NOT random or incident-balanced sampling. All unscanned rows and missing near-event coverage prevent a full-incident adequacy claim. A full scan is supported with no row cap, but requires a separate recorded run. This cap was refined before execution to bound NetworkX memory while testing all schema families and two labelled scopes per scenario.

Inspect all label rows independently of the telemetry cap. Audit all available headers. Preserve unknown source columns, report them, and fail strict replay on unexpected headers. Reject malformed rows explicitly; never impute values/times/units. Retain duplicate records with unique row provenance and flag them.

Construct the operational graph using only telemetry. Derive CALLS evidence only from uniquely resolved parent spans in the same trace; report missing/ambiguous parents. Keep root labels in a separate evaluation graph. Do not turn component labels into telemetry-observed entities or infer dependencies from roots. No causal edges, fabricated hypotheses, service aliases, units or durations.

Run each scenario twice; compare canonical and graph digests. Execute fixtures plus a local-dataset integration test. Report record conservation (selected source rows = mapped + rejected; wide metric rows expand to multiple observations), unresolved references and source-field preservation. Distinguish preservation from semantic understanding.

Acceptance: all four scenarios represented deterministically; zero silently dropped fields, zero fabricated causal claims, explicit rejections; no UNKNOWN semantics or coverage gaps critical to the proposed downstream task. Failure of the last criterion blocks downstream readiness, even if implementation tests pass.

No next experiment until report, results and decision reviewed. Protocol/config source hashes captured at execution; not a committed/protected freeze.
