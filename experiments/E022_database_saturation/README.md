# E022 — XP019 local database write-contention intervention

This experiment invokes the existing DCE OTLP intake application against an experiment-local SQLite database. Each synthetic valid request is sent once without contention, once while a second connection holds `BEGIN IMMEDIATE`, then retried after lock release. All traffic uses an in-process ASGI transport; no external socket or Docker service is involved.
