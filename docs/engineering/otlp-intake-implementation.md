# OTLP intake implementation note

Date: 2026-10-03. Scope: local engineering attachment slice. This is a new implementation note and does not change any E003 experiment record or gate.

## Delivered capability

`dce_foundation.ingest` now exposes an OTLP/HTTP binary protobuf receiver for metrics and traces. It writes each accepted request to a local SQLite append log before returning success. The log keeps payload bytes, SHA-256, receipt time, original event-time range, source `service.name`, signal type and counts. Receipt sequence provides deterministic replay order.

The replay CLI renders a bounded source view. In the verified direct path it displayed the original metric `dce.demo.requests`, unit `{request}`, service `dce-demo-service`, trace ID, span ID and source event timestamps. The raw protobuf remains the durable source of truth; this view makes no feature, unit or topology inference.

## Verified locally

- `python -m pytest -q -p no:cacheprovider tests/test_otlp_intake.py`: 8 passed.
- Full suite: 47 passed.
- A real OpenTelemetry Python SDK emitter sent a metric and request span to Uvicorn on `127.0.0.1:4318`.
- The server was stopped before the replay command ran. SQLite retained and replayed the three new receipt rows after restart: two metric exports and one trace export. The periodic metric exporter can emit more than one batch for one counter update; each accepted delivery is retained.
- Tests cover binary success responses, event/source metadata, receipt replay, duplicates, malformed protobuf, unsupported content type, payload limit, unavailable storage and health reporting.

## Pending qualification

The local environment has the OpenTelemetry Python SDK/exporter packages but no `otelcol-contrib` command. `examples/otlp-intake/collector.yaml` and `collector_emitter.py` are ready for the Collector path, but that path has not been executed here. TLS, authentication, OTLP JSON/gzip, logs/profiles, partial success, Collector retry behavior, throughput, disk exhaustion recovery, PostgreSQL and deployment packaging are also unqualified.

## Run commands

See [the demo README](../../examples/otlp-intake/README.md) for the direct and Collector commands. The default local database is `data/raw/intake/dce-intake.sqlite3`, which is ignored as raw derived data. Use `DCE_INTAKE_DB` for a different local path.

## Current product boundary

This creates a usable local attachment point and durable replay log. It does not start feature extraction, a graph, anomaly detection, root-cause analysis, planning or remediation. E003 remains pending human review.
