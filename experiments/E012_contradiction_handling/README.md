# E012 — contradiction handling pilot

Planning alignment: XP009. This controlled synthetic pilot compares support-only diagnosis ranking against an explicit observed-healthy contradiction rule and abstention. It tests logic behavior on a small frozen fixture; it does not test DCE application integration or real RCA.

All inference inputs, evaluator labels, predictions, and run records stay local. Labels are stored separately from inference fixtures and opened only after prediction sealing.

Run from repository root:

```powershell
python experiments/E012_contradiction_handling/scripts/run_predictions.py
python experiments/E012_contradiction_handling/scripts/evaluate.py
python experiments/E012_contradiction_handling/scripts/independent_audit.py
```
