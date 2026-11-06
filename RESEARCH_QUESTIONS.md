# DCE research questions

Status: open research agenda. No question below is considered answered by the scaffolding.

| ID | Question | Evidence required | Experiment |
|---|---|---|---|
| RQ-01 | Does hybrid reasoning improve root attribution over the strongest independent baseline at the same alert budget? | Paired held-out incidents, ablations, uncertainty intervals | E001 baseline reproduction; follow-up design after review |
| RQ-02 | Are neural and SLO onset estimates comparable, and does temporal reasoning improve attribution? | Explicit onset source and uncertainty; timing-on/off comparison | E002 reserved |
| RQ-03 | How robust is detection to workload drift and missing telemetry? | Held-out load levels, missingness patterns, precision/recall and coverage | Unassigned |
| RQ-04 | Does the model generalize to unseen services and topologies? | Held-out topology protocol, explicit baseline adaptation budget | Unassigned |
| RQ-05 | Can dependency reasoning distinguish symptoms, multiple origins and shared infrastructure faults? | Intervention-labeled testbed incidents and negative controls | Unassigned |
| RQ-06 | When should the system abstain, and is reported confidence calibrated? | Coverage/risk curves, calibration and contradictory evidence fixtures | Unassigned |
| RQ-07 | Are decisions reproducible across replay, model promotion and worker recovery? | Pinned artifacts, restart/replay tests, decision/evidence comparisons | Unassigned |
| RQ-08 | Do recovery recommendations improve incident outcomes safely? | Reviewed runbooks; later controlled intervention protocol | Unassigned; execution out of initial scope |

Each experiment maps to one or more research questions. New experiments receive fresh IDs from the index;
never reuse a cancelled ID or retroactively redefine a completed hypothesis.
