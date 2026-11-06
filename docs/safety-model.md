# Safety model

R0 experiments are offline. Initial runtime recommendations require operator review; autonomous remediation is outside current scope.
Reject incompatible artifacts and preserve degraded/unknown processing status. Treat unsupported confidence and stale telemetry as explicit limitations.

Validate payload/cardinality limits, environment authorization, artifact integrity, secret redaction and webhook destinations
when runtime adapters are implemented. Review operator feedback before training; no automatic online self-modification.
Keep raw sensitive telemetry and credentials out of experiment logs committed to Git.

Future intervention protocols specify scope, stop conditions, approval, rollback, blast-radius budget and post-action verification.
These are proposed requirements; repository scaffolding does not establish operational safety controls.
