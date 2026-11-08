# Hypothesis

When SQLite's writer lock is held beyond the intake connection's configured timeout, the DCE intake will return a retryable 503 without acknowledging durability. After lock release, retrying the same batch will return success and persist it as a duplicate linked to the original durable batch.
