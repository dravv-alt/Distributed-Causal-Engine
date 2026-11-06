# Request rereading checkpoints

Before implementation: reread the four remaining gates and the user's revised A–H completion table. UNKNOWN metrics are acceptable when explicit; criterion differs from historical AM001 and is frozen in a new amendment.

After implementation: reread incident-window and leakage requirements. Retrieval selects all resources from scenario/time windows; it never selects by labelled root. Ground truth enters only the evaluator coverage/association pass. Post-fault context is audit-only. Trace edges require both spans at/before query cutoff; unknown-validity workbook edges are excluded from inference.

After tests: 13 new qualification tests and all 89 repository tests passed. Tests include complete-file late mixed-scale detection, exact EOF hash, date and time bounds, explicit UNKNOWN registry entries, label mutation invariance, raw-name/metadata exclusion, post-cutoff parents, ambiguous parents and source-based query association. No gates or selection were changed after seeing results.

During execution: original records and v1/v2 source remain unchanged. The new process streams complete CSVs, stores compressed incident-window rows and writes a completed file profile immediately. Resource limits are explicit. No raw deletion, RCAEval, RCA model or future stage is part of this execution.
