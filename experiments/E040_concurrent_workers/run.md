# E040-R001 run record

Single worker completed 100/100 tasks; three concurrent workers completed 100/100 matched tasks. Duplicate execution count was zero in both groups. Ownership mismatches: zero. In the stale-owner challenge, the lease advanced from fence 1 to 2; stale commit was rejected and new-owner commit accepted. SQLite integrity was `ok`.

The instrument is an isolated local SQLite/thread simulator. The task is synthetic and the DCE application queue/worker was not exercised; this is not evidence of production concurrency safety or throughput.
