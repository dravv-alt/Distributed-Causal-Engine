# E025-R001 interpretation — XP022

- Best-action match rate: **99.7%** across 600 generated cases.
- Pairwise predicted-versus-controlled action ranking consistency: **81.8%**.
- Mean absolute recovery error: **0.143**, compared with **0.384** for the zero-recovery baseline.
- Per-action mean generated recovery was approximately 0.38; the dataset balances the three mechanisms, so this overall average hides each action's larger recovery in its matching mechanism subgroup.

The independent audit recomputed all action scores from inference inputs and all reported rankings against evaluator-only outcomes.

## Limits

Action indicators were generated to be informative about the mechanism, and the matching action was assigned a high expected recovery by construction. Noise explains imperfect pairwise ranking and recovery prediction. No scaling, repair, rerouting, or remediation was executed against DCE or a running service. This does not support a real action recommendation, causal effect estimate, or safety claim.
