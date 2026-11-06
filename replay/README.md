# Replay

Reserved project boundary. Existing R0 implementation remains in dce-r0/dce; no runtime or artifacts are supplied here by scaffolding.
New work must reference a registered experiment or architecture decision, with code/configuration and artifact provenance.

E003's implementation is `src/dce_foundation/replay/openrca.py`. From the repository root set PYTHONPATH=src
and run `python -m dce_foundation.replay.openrca --incident Bank@2 --max-rows-per-file 2000`.
No actions, model inference or RCA reasoning are performed. Read docs/E003-implementation-report.md before using its outputs downstream.
