# Local OTLP intake demo

This is a local attachment demonstration. It creates no RCA result and requires no OpenRCA data.

Install the explicit demo dependencies:

```powershell
python -m pip install -r requirements-ingest.txt opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
```

Start DCE in one terminal:

```powershell
$env:PYTHONPATH = 'src'
uvicorn dce_foundation.ingest.app:app --host 127.0.0.1 --port 4318
```

Direct path: in a second terminal run `python examples/otlp-intake/emitter.py`. Inspect durable receipt order with:

```powershell
$env:PYTHONPATH = 'src'
python -m dce_foundation.ingest.replay
```

Collector path: install an OpenTelemetry Collector distribution, start it with `otelcol-contrib --config examples/otlp-intake/collector.yaml`, then run `python examples/otlp-intake/collector_emitter.py`.

Restart the DCE process and repeat the replay command. The records stay in `data/raw/intake/dce-intake.sqlite3`. Sending the same protobuf again creates a new receipt sequence with `duplicate_of_sequence` set. This is at-least-once acceptance.
