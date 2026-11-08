# E023-R001 protocol — frozen before implementation

Date 2026-11-07 (Asia/Calcutta). Stage XP020. Generate 600 cases (300 direct effect, 300 common-cause/no direct effect), 100 observational rows and 40 matched interventional contexts per case. Seed 22020. Mechanism labels and true effect remain evaluator-only.

- Observational baseline: OLS slope of Y on A with intercept.
- Explicit structural model: OLS coefficient of A in Y ~ A + measured U + intercept. Identification assumptions: linear additive mechanism, U observed and adequately measured, independent errors conditional on A/U, no interference, consistent interventions.
- Reference: mean paired potential-outcome difference from synthetic matched intervention contexts, evaluator-only.
- Causal-link decision threshold: estimated effect >=0.50. Report effect RMSE versus intervention reference, link/path accuracy, sensitivity, specificity, and Wilson intervals.
- Assumption sensitivity: paired change in estimate and link decision when measured U is omitted from the structural model.
- Prediction script gets observational A/U/Y but not mechanism labels or intervention outcomes. Seal predictions before evaluation; independent audit recomputes OLS and metrics.

Simulation assumptions are deliberately explicit. Results do not identify a real causal effect or validate the assumptions in DCE.
