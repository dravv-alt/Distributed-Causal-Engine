# E033-R001 protocol — frozen before implementation

Date 2026-11-07 (Asia/Calcutta). Stage XP030. Generate 300 cascades, seed 33030, with the chain database degradation→service-B slowdown→service-A timeout→retry storm. Observation onsets receive jitter, while causal edges remain explicitly provided.

- Propagation method: choose the symptomatic node with greatest downstream reachability and recommend root repair.
- Independent-symptom baseline: recommend individual actions for service slowdown, timeout, and retry queue; do not repair database.
- Sandbox transition model: root repair clears all cascade symptoms; symptom-only actions temporarily suppress their targeted symptom, but the active database fault regenerates downstream symptoms at the next check.
- Report root selection, action count, propagation-path correctness, first-step symptom clearance and stable recovery at three simulated checks. True root remains evaluator-only.
- No real faults, retry storm, service workload, or action execution.
