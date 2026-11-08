# E040-R001 provenance review — 2026-11-08

This additive review preserves the original records and does not qualify DCE's application queue.

## Integrity checks

- Recomputed all 11 artifact-manifest entries; every listed file exists and matches its recorded size and SHA-256 hash.
- Independently opened `workers.sqlite` in read-only/query-only mode. Integrity is `ok`; 201 tasks, decisions, and execution rows are present; there are no duplicate task executions or ownership mismatches. The stale case is done under `worker-new` with fencing token 2.
- The directory also contains a zero-byte WAL and 32 KiB shared-memory sidecar. These are not listed in the artifact manifest; the main SQLite database is covered.

## Result and construction limits

The stored run reports 100/100 single-worker tasks and 100/100 tasks across three local Python threads, with no duplicate executions. The stale-owner challenge advanced fencing from 1 to 2, rejected the old worker's commit, and accepted the new worker's commit.

This exercises a local SQLite `BEGIN IMMEDIATE` lease/claim simulator. SQLite serializes the write transactions; the workers are threads in one process, not distributed workers. The run does not exercise DCE's actual queue, worker, database configuration, process boundaries, network partitions, scheduler, or production load. It reports no throughput or latency measurement, and the single stale-owner challenge does not characterize broad failure conditions.

## Provenance and governance discrepancy

Artifact hashes and read-only database counts are consistent. A frozen Git revision/clean source snapshot at run time is not recorded; that provenance remains unknown.

The E040 additive amendment maps XP037 to this local pilot. The permanent index is unchanged, and no conclusion about DCE production concurrency safety follows.

## Bounded disposition

The local threaded SQLite instrument preserved its own task/decision and fencing checks for the declared cases. Actual DCE concurrency safety and queue capacity remain UNKNOWN.
