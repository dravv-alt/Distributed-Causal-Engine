# E012 execution ledger

## E012-R001

The first prediction launch failed before inference because the repository package was absent from the interpreter import path. The failure is retained in `results/E012-R001/execution-attempt-001-failure.json`; no labels were read and no prediction artifacts were created by that attempt.

The runner was then made to load the local `src/` tree, with no dependency installation or network access. The frozen six-case synthetic protocol ran in this order:

```powershell
python experiments/E012_contradiction_handling/scripts/run_predictions.py
python experiments/E012_contradiction_handling/scripts/evaluate.py
python experiments/E012_contradiction_handling/scripts/independent_audit.py
```

Predictions were hashed before evaluator labels were opened. The independent recomputation returned PASS. Results and hashes are under `results/E012-R001/`.
