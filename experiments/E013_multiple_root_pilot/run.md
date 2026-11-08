# E013 execution ledger

E013-R001 ran locally in this sequence:

```powershell
python experiments/E013_multiple_root_pilot/scripts/run_predictions.py
python experiments/E013_multiple_root_pilot/scripts/evaluate.py
python experiments/E013_multiple_root_pilot/scripts/independent_audit.py
```

The six label-blind predictions were sealed before evaluator labels were opened. The independent audit reproduced all rankings, aggregate metrics, prediction hash, and label hash. Complete outputs and provenance are in `results/E013-R001/`.
