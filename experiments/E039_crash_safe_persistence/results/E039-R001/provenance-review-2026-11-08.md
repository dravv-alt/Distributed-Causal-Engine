# E039-R001 provenance review — 2026-11-08

This additive review preserves the original run, protocol, and register.

## Integrity checks

- Recomputed all 12 artifact-manifest entries; each listed file exists and matches its recorded size and SHA-256 hash.
- Independently opened the SQLite file in read-only/query-only mode. `PRAGMA integrity_check` returned `ok`; there are 72 inputs, decisions, outbox rows, and deliveries, with zero unsent outbox rows. All 24 lease rows have fencing token 2.
- The directory also contains a zero-byte `-wal` file and a 32 KiB `-shm` sidecar. These sidecars are not listed in the artifact manifest; the manifest does cover the main SQLite file.

## What the run exercised

The run produced the declared 72 trial records across six named crash points, with one decision and one delivery per case. However, source inspection shows these are connection close/reopen simulations within one Python process, not abrupt process termination or power-loss injection. The `before_commit` case rolls back an open SQLite transaction; other cases commit state and then close/reopen a connection. The two lease cases use the same branch and sequence, so they do not represent distinct lease timing conditions.

The stored audit checks final table counts, uniqueness, unsent outbox count, and SQLite integrity. The results support those final local-database invariants for this script. They do not prove recovery from an actual process crash, transaction interruption by OS failure, or DCE's operational persistence path.

## Provenance and governance discrepancy

Artifact hashes and the read-only database check are consistent. A frozen Git revision/clean source snapshot at run time is not recorded; that provenance remains unknown.

The E039 additive amendment maps XP036 to this isolated SQLite instrument. The permanent experiment index is unchanged; no DCE application persistence or worker implementation was tested.

## Bounded disposition

This is a local SQLite connection-restart/outbox/fencing simulator, not a crash-safety validation of DCE. Claims about application crash recovery and concurrent ownership remain UNKNOWN.
