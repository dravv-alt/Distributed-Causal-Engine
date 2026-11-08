# E031-R001 run record

- Planning stage XP028.
- 240 in-memory scenarios: 120 successful transitions and 120 injected partial/wrong transitions across restart, scale, reroute.
- Prediction process did not read the environment failure schedule. Sandbox executor alone applied the injected outcomes. Controller compared expected and observed state, requested replan on mismatch, and produced rollback snapshots.
- 120/120 injected failures were detected; 0/120 successful cases were false alarms; all 120 injected cases requested re-diagnosis and restored the snapshot in the simulation.
- Independent audit passed. No external rollback or action was executed.
