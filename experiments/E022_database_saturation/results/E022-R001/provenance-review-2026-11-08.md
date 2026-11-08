# E022-R001 provenance review — 2026-11-08

This additive review records local integrity checks and does not change the experiment result or disposition.

## Integrity checks

- All 22 artifact-manifest entries match their recorded byte counts and SHA-256 hashes.
- The raw-run hash matches `evaluation.json`; the retained SQLite database hash matches the independent-audit record.
- The saved independent audit reports PASS: 5/5 controls succeeded, 5/5 lock interventions returned retryable 503 responses, 5/5 post-release retries were accepted and linked to durable originals, and SQLite integrity was `ok`.

## Reproducibility and data boundary

The run retains content hashes and the database file but no Git commit or dirty-tree state. Experiment sources are currently untracked, so a Git-frozen pre-run snapshot cannot be verified from the repository. The request payloads and disposable SQLite database stayed local; execution used in-process ASGI and no external socket, Docker service, or remote compute.

## Interpretation boundary

This is evidence about five matched writer-lock trials against the local SQLite-backed DCE intake. It demonstrates the local retry and duplicate-linking contract under that lock condition. It does not establish distributed database saturation, downstream RCA effects, or multi-service behavior; Docker Desktop access was unavailable and no Compose workload was present.
