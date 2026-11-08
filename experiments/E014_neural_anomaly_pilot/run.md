# E014 execution ledger

## E014-R001

Predictions were generated from blind metrics only, using the frozen 35% fit / 15% calibration / 50% scoring split. Nine per-case autoencoders and the statistical baseline were run on CPU. The prediction file was sealed before the evaluator opened RCAEval index labels.

Commands:

```powershell
python experiments/E014_neural_anomaly_pilot/scripts/run_predictions.py
python experiments/E014_neural_anomaly_pilot/scripts/evaluate.py
python experiments/E014_neural_anomaly_pilot/scripts/independent_audit.py
python experiments/E014_neural_anomaly_pilot/scripts/independent_audit_v2.py
```

The first independent audit attempt is preserved in `results/E014-R001/independent-audit-attempt-001-note.json`; it failed its structural comparisons because of mismatched report keys, while aggregate metrics matched. The corrected independent audit is `independent-audit-v2.json` and passed all aggregate, per-case, alignment, index-hash, and prediction-seal checks.

The run emitted NumPy warnings for all-NaN training slices and optional pandas dependency warnings (`numexpr` and `bottleneck`) during label evaluation. The runner handled all-NaN features using the frozen median fallback and mask indicators; the computation completed. No dependency installation or network access occurred.
