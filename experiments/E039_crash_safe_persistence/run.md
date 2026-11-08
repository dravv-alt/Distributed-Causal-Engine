# E039-R001 run record

72 cases across six crash points (12 each). After reopen and replay, every case had exactly one decision and one delivered notification; SQLite integrity was `ok` for all cases. The 24 stale lease writes were rejected after fencing token advancement.

The database is isolated at `results/E039-R001/crash-lab.sqlite`. No DCE operational database or service was used. This tests a toy transaction/outbox protocol, not the application's persistence implementation. No approved numeric threshold exists.
