# E024-R001 protocol — frozen before implementation

Date 2026-11-07 (Asia/Calcutta). Stage XP021. Generate 1,000 randomized training observations and 400 held-out baseline contexts using seed 24021. Outcome equation: Y=1.0A+0.8U+epsilon, U~N(0,1), epsilon~N(0,0.5). Fit OLS with intercept, A and U using training observations only.

- At inference, provide the fitted coefficients and each held-out baseline's measured U and observed Y under do(A=0); predict Y under do(A=1).
- Evaluator-only file holds the separate matched do(A=1) outcome for each context. Do not open it before prediction sealing.
- Reference baseline predicts no treatment change (Y(do1)=observed Y(do0)).
- Report MAE/RMSE, signed effect direction and consistency, path/mechanism direction accuracy, and paired bootstrap intervals (10,000, seed 24022) for model-minus-baseline absolute error.
- Fixed assumptions: model form and mechanism invariant, U fully measured, no hidden confounding or interference, stable noise distribution, treatment consistency. Synthetic outcome pairs are generated under the same U; this is a simulation oracle, not an observed real counterfactual.

Local NumPy CPU only, no network. The evaluator intervention outcomes remain separate from inference.
