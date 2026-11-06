# Evaluation protocol

Register question, hypothesis, metrics, controls and decision criteria before execution. Freeze code/config/data versions
and seeds. Separate train/calibration/test by time with context-plus-horizon embargo, and report held-out seeds/topologies.
No ground truth, future observations or resolution metadata may enter inference.

Compare threshold-only, independent neural-only, symbolic-only and hybrid at comparable alert budgets.
Audit implementation boundaries: R0's neural_only variant still uses shared topology/fusion logic with SLO triggers disabled;
it is not an independent neural RCA model. Report this naming limitation rather than presenting it as a pure ablation.

Match incidents one-to-one within preregistered event intervals; report false positives, duplicates and unmatched true events.
Report event coverage separately from incident recall; selecting a best later diagnosis within a ground-truth interval
is retrospective accuracy, not first-alert accuracy. Report both when relevant.

Metrics: precision/recall, false alerts per environment-day with exposure, first detection delay, first-alert and retrospective
Top-1/Top-3/root-set accuracy, abstention coverage, calibration if probabilities are exposed, and paired uncertainty intervals.
Stratify faults, concurrency, load, missingness and topology changes. Include normal/negative controls and failure cases.

The proposed hybrid gain gate is at least five percentage points above the strongest comparable baseline;
this is a research target, not achieved performance. Missing evidence means pending, not passed.
