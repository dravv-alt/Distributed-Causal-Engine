# E022-R001 protocol — frozen before execution

Date 2026-11-07 (Asia/Calcutta). Stage XP019. Scope: five matched request pairs to the existing local DCE OTLP intake and a disposable experiment-local SQLite file.

- Build five distinct valid OTLP metrics payloads with stable service identity and unique trial attribute.
- For each payload, send one no-lock control request and record status/latency.
- Hold an external SQLite `BEGIN IMMEDIATE` writer transaction on the same file while sending the matched request. Do not write data from the lock-holder. The implementation's 5-second SQLite connection timeout is part of the intervention; the expected result is a retryable 503.
- Release lock and retry the identical payload. Require 200, durable row, matching hash, and `duplicate_of_sequence` pointing to the original control record.
- Report counts for control, contention, retry and durable records; each trial is descriptive (n=5), no population inference.
- Keep database, inputs, raw responses and run metadata inside the new experiment folder. No production systems, network traffic, Docker, or remote compute.

The intervention is a local SQLite writer-lock contention scenario, not proof of distributed database saturation behavior. Docker Compose could not reach its engine at protocol freeze time (`docker info` reports access denied); no compose file exists in the workspace.
