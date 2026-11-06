# Planned source boundaries

The domain, telemetry, graph, reasoning, causal, planning, fusion, inference, persistence and workers directories are reserved.
The delivered R0 executable package remains in ../dce-r0/dce/src/dce. Migration requires a registered experiment/decision and regression evidence; no source was moved here.

E003 adds `dce_foundation/`, a separate package containing dataset-independent domain values, event time,
the OpenRCA adapter, typed operational/evaluation graphs, validation, inspection and replay.
It does not migrate or modify R0. The domain/telemetry/graph concepts live inside this explicit namespace;
the generic root boundary directories remain reserved. Downstream readiness is blocked pending E003 review.
