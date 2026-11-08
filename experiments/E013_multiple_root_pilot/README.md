# E013 — simultaneous-root pilot

Planning alignment: XP010. This synthetic pilot checks whether a fixed root-set method can represent two independent roots without forcing every case to one root. Three multi-root fixtures and three single-root controls compare the method with a unique-single-root baseline.

The pilot does not validate DCE on real incidents. Inference fixtures and evaluator roots are separate; predictions are sealed before labels are read. Everything is run locally.

```powershell
python experiments/E013_multiple_root_pilot/scripts/run_predictions.py
python experiments/E013_multiple_root_pilot/scripts/evaluate.py
python experiments/E013_multiple_root_pilot/scripts/independent_audit.py
```
