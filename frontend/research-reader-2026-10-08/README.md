# Research notebook preview — 8 October 2026

Additive, read-only presentation of E001–E004. Existing frontend and scientific records are preserved.

From repository root, serve only localhost:

```powershell
python -m http.server 8080 --bind 127.0.0.1
```

- Preview: http://localhost:8080/frontend/research-reader-2026-10-08/
- Existing current cockpit: http://localhost:8080/frontend/research-cockpit/
- Audit: `docs/FRONTEND_AUDIT_2026-10-08.md`

Serve the repository root so original evidence links work. `records.json` is a dated snapshot, with build-time hashes. It does not watch source changes, execute experiments, approve decisions or refresh itself.

The preview was built with `python -m scripts.build_research_reader_20261008`. Its exclusive output creation deliberately refuses reruns that would overwrite the dated snapshot. Future snapshots require separate paths/authorization; the historical v1 builder does not build this reader.
