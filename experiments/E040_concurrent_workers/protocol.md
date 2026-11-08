# E040-R001 protocol (2026-11-07)

Run 100 synthetic tasks through one worker and 100 matched tasks through three local worker threads using SQLite. Claim under `BEGIN IMMEDIATE`; each lease carries an incrementing fence. Record execution attempts and unique decisions. Separately transfer one expired task lease from worker-old (fence 1) to worker-new (fence 2), attempt stale commit, and require rejection. Compare completed tasks, duplicate execution, ownership and stale rejection. No external system or application queue is used. Thresholds are descriptive; none approved.
