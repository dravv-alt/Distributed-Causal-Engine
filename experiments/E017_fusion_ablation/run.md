# E017-R001 run record

- Stage: XP014 fusion ablation.
- Dataset: 600 deterministic synthetic 10-service cases; generated inputs and evaluator labels are separate.
- Arms: neural-only, symbolic-only, neural+topology, neural+topology+temporal, full fusion.
- Execution: local Python/NumPy CPU scripts. The `orx` OpenResearch CLI is not installed in this workspace; no OpenResearch remote or managed compute was used. The scripts contain no network calls.
- Labels were not loaded during prediction; prediction hash was sealed before evaluation.
- Independent audit passed all five-arm metric recomputations and coverage checks.
- Results and limitations: `results/E017-R001/evaluation.json` and `interpretation.md`.

This is a synthetic method-mechanics pilot only. It does not evaluate RCAEval or the DCE application.
