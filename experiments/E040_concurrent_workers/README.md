# E040 / XP037 concurrent-worker pilot

Local SQLite/thread simulator comparing one worker against three concurrent workers on matched-sized synthetic queues. Includes a controlled lease-expiry/fencing challenge. It does not exercise DCE's application worker or PostgreSQL queue.
