# E009-R001 run summary

The frozen topology-only baseline ran on nine selected, blinded RCAEval cases with labels opened only after prediction sealing. Independent graph/metric audits passed. Five cases lacked traces, so both topology and uniform baselines abstained on them; root candidate coverage was 4/9.

Topology shared-callers scored 0.0% tie-aware Top-1 and 7.4% Top-3, versus 4.3% and 12.9% for graph-disabled uniform. The sample is selected and too small for population inference. Detailed execution failures/recovery, predictions, evaluation, interpretation, and hashes remain under `results/E009-R001/`.
