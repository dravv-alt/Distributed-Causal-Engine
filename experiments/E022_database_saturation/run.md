# E022-R001 run record

- Planning stage: XP019.
- Application: existing `src/dce_foundation/ingest/app.py` and `IntakeStore` in `src/dce_foundation/ingest/store.py`.
- Five payloads were sent via in-process ASGI transport in matched control, writer-lock, and post-release retry conditions.
- Results: control 5/5 returned 200; locked writer 5/5 returned 503 after a median 5.50 s; post-release retry 5/5 returned 200. All five retries were durably stored as duplicates linked to the original records; SQLite integrity check returned `ok`.
- Local disposable SQLite file only. No network or remote compute.
- Compose availability audit: Compose CLI exists, but Docker Desktop engine returned access denied; no compose file was present. This is a component-level SQLite intervention, not multi-service saturation.
- Independent audit passed: `results/E022-R001/independent-audit.json`.
