# E014 — neural anomaly detection pilot

Planning alignment: XP011. This local pilot compares a small PyTorch autoencoder with a robust statistical detector. Each method uses an unsupervised early-prefix fit and a later-prefix calibration segment, then scores the remaining chronological suffix of each selected case. Evaluator labels are opened only after prediction sealing.

The cases were selected for schema coverage, not as held-out incidents. All metric column semantics remain unqualified. The result is descriptive and cannot establish general RCA or detector performance.

```powershell
python experiments/E014_neural_anomaly_pilot/scripts/run_predictions.py
python experiments/E014_neural_anomaly_pilot/scripts/evaluate.py
python experiments/E014_neural_anomaly_pilot/scripts/independent_audit.py
```
