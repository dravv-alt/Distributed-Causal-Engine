# Minimal OTLP intake slice

Status: implemented local engineering slice; it does not alter E003 evidence or authorize downstream research work.

## Scope

The receiver accepts OTLP/HTTP binary protobuf requests at `/v1/metrics` and `/v1/traces`, validates the signal-specific request type, derives only transport/source metadata, then writes the original payload and metadata to SQLite. Acknowledgment occurs after SQLite commits. It offers `/healthz` and a receipt-order replay command.

It does not accept OTLP JSON, logs or profiles. It does not normalize metrics, construct a graph, extract features, make RCA claims, or perform inference. Metrics retain original OTLP payloads so units, aggregation temporality and histogram details can be interpreted by a later reviewed mapper. Trace identifiers and parent IDs remain in their original payloads. Replay also renders a bounded inspection projection with metric name/unit/type and trace/span/parent IDs; it does not alter source payloads.

## Durable acceptance contract

SQLite uses WAL mode and `synchronous=FULL`. Each accepted request receives a monotonic sequence after a durable transaction containing:

- signal type, UTC receipt time, payload and SHA-256;
- resource `service.name` values, using `UNKNOWN_SERVICE` when absent;
- earliest/latest source event timestamp observed in supported point/span fields;
- source item/resource counts and a small nonsemantic summary;
- a duplicate reference when the same payload hash appeared earlier.

The service has **at-least-once** semantics. It retains retry deliveries as new rows and marks their first matching payload sequence. Payload hashes detect byte-identical requests only; they do not deduplicate semantically identical batches with different encoding/order.

Full success produces the matching empty OTLP protobuf response with HTTP 200 and `application/x-protobuf`. Bad type/encoding or malformed protobuf returns a protobuf `google.rpc.Status` with HTTP 400/415/413. A failed durable write returns HTTP 503, which is retryable for OTLP/HTTP. The receiver does not send partial success: a batch is either durably retained in full or rejected in full.

## Files

| Path | Purpose |
|---|---|
| `src/dce_foundation/ingest/app.py` | HTTP application and protocol status behavior |
| `src/dce_foundation/ingest/otlp.py` | Protobuf decode and noninferential metadata extraction |
| `src/dce_foundation/ingest/store.py` | SQLite append log, duplicate visibility and replay |
| `src/dce_foundation/ingest/replay.py` | CLI inspection in receipt sequence |
| `examples/otlp-intake/` | direct emitter and Collector configuration/demo |
| `requirements-ingest.txt` | explicit runtime requirements, pending a reviewed dependency lock |

## Run locally

```powershell
python -m pip install -r requirements-ingest.txt opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
$env:PYTHONPATH = 'src'
uvicorn dce_foundation.ingest.app:app --host 127.0.0.1 --port 4318
```

In another terminal:

```powershell
python examples/otlp-intake/emitter.py
$env:PYTHONPATH = 'src'
python -m dce_foundation.ingest.replay
```

For the Collector route, run an OpenTelemetry Collector with `examples/otlp-intake/collector.yaml`, then use `collector_emitter.py`. Restarting Uvicorn and replaying demonstrates retained batches. The default SQLite path is ignored under `data/raw/intake/`; set `DCE_INTAKE_DB` to select another local path.

## Limits and next proof

Default limits are 4 MiB per request and 128 MiB for the local SQLite file. These are local protective defaults, not throughput qualification. Compression, authentication, TLS termination, partial-success reporting, schema-specific metric mapping, database migrations, PostgreSQL, queue/workers and Collector deployment packaging are outside this slice.

The acceptance proof requires fixture tests plus a real direct-emitter path and Collector round trip. Record those results as a separately authorized engineering test; do not treat static tests as a Collector integration result.
