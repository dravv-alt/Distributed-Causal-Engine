# E024-R001 run record

- Planning stage XP021.
- Model: OLS trained on 1,000 synthetic randomized observations; 400 held-out baseline contexts.
- Prediction input excluded the intervention outcomes; the prediction seal records input/model/training hashes.
- Local NumPy CPU only; no network or remote execution.
- Independent audit refit OLS and recomputed all 400 counterfactual predictions and errors; passed.
- See `results/E024-R001/evaluation.json` for metrics and `interpretation.md` for assumptions/limits.
