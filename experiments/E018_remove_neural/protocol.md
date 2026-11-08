# E018-R001 protocol — frozen before implementation

Date: 2026-11-07 (Asia/Calcutta). Stage: XP015. Scope: synthetic neural-branch ablation only.

## Inputs and controls

- Generate 600 cases with 10 services each using the frozen generator function in `experiments/E017_fusion_ablation/scripts/generate_fixtures.py`, seed 28015. Retain labels separately from inference inputs.
- **Full fusion:** arithmetic mean of within-case average-rank scores for neural, topology, temporal and symbolic modalities.
- **Neural-disabled:** identical method and cases, but average only topology, temporal and symbolic scores. No neural values are read for this arm.
- Scoring/tie order, abstention threshold 0.05, CPU execution, and all other transforms remain fixed.
- Metrics: Top-1/Top-3/MRR, paired Top-1 and MRR differences with 10,000 paired bootstrap resamples (seed 18015), false diagnosis among covered cases, abstention, coverage, explanation and generated-path accuracy.
- Calibration diagnostics: apply softmax to each arm's rank scores divided by fixed temperature 0.1; report multiclass Brier score and 10-bin ECE. These transformed rank scores are not calibrated application probabilities.

Prediction must not open labels; seal prediction hash before evaluation. An independent script recomputes all published metrics from the sealed predictions and evaluator-only labels. All conclusions are limited to this synthetic generator.
