# Reproduce the bounded semantic validation

From repository root in PowerShell, with Python 3.12.6 and NetworkX 3.4.2:

```powershell
$env:PYTHONPATH = 'src'
& .\.venv-e002\Scripts\python.exe -m pytest -q -p no:cacheprovider tests\test_representation_v2.py
& .\.venv-e002\Scripts\python.exe -m dce_foundation.representation_v2.audit --config experiments\E003_domain_model_adequacy\remediation\2026-10-03\configuration.json --output <new-empty-path>
```

The audit refuses an existing output directory. It records a source snapshot and preflight before corpus processing. Use a new directory for every attempt. Configuration declares the first intended validation V001; executed summary identifies its actual directory. A validation command can complete successfully while semantic gates remain PARTIAL/FAIL.

Reports `coverage-*.json` contain timestamp/schema/identity/trace/missingness/duplicate/coverage profiles per file; `graph-*.json` contains typed operational topology; `incident-coverage.json` is evaluator-only incident coverage; `leakage-audit.json` names remaining checks; `artifact-manifest.json` hashes outputs. SQLite dispositions provide rejected-row evidence without dumping sensitive raw rows into terminal output.

Library replay: `dce_foundation.representation_v2.store.replay(connection)` yields deterministic event-time ordered records. This is full provenance replay, not the inference view. `openrca.inference_view(observation, QueryWindow(...))` projects allowlisted fields and excludes future observations. The existing v1 CLI is unchanged and continues to use v1 semantics.

The current audit CLI implements the bounded protocol only. Whole-file/incident-context scans require separately recorded scope and measurements; no full-scale qualification is implied by disk-backed storage.
