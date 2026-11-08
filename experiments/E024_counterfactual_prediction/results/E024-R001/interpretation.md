# E024-R001 interpretation — XP021

| Method | MAE | RMSE | Effect-direction consistency | Positive-effect mechanism-path accuracy |
|---|---:|---:|---:|---:|
| Fitted counterfactual model | 0.377 | 0.473 | 94.8% | 83.3% |
| No-change baseline | 1.058 | 1.221 | — | 0% |

The model-minus-baseline paired MAE difference was -0.681 (95% bootstrap interval -0.744 to -0.616). OLS estimated the treatment coefficient as 1.006. Independent audit refit the model on the training-only inputs and independently checked every sealed prediction against the held-out intervention outcomes.

## Limits

The linear model is correctly specified by the synthetic generator, U is measured without error, and train/test mechanisms are identical. The evaluator file contains paired synthetic potential outcomes, which cannot both be observed for the same real unit. The apparent improvement is expected when the simulator and estimator share the same assumptions. This is not evidence of causal self-healing or outcome prediction in DCE.
