# E009-R001 execution sequence

Commands ran from the repository root in this order:

```powershell
python experiments/E009_rcaeval_topology_baseline/scripts/run_predictions.py
python experiments/E009_rcaeval_topology_baseline/scripts/independent_audit.py
python experiments/E009_rcaeval_topology_baseline/scripts/evaluate_labels.py
python experiments/E009_rcaeval_topology_baseline/scripts/evaluate_labels_after_map_recovery.py
python experiments/E009_rcaeval_topology_baseline/scripts/independent_evaluation_audit.py
```

The first evaluator stopped on an incomplete mapping before opening the label index. That failure is preserved. The second evaluator used the exact existing one-case selection manifest plus the fixed eight-case group map. The first independent metric-audit run failed due to its own abstention-count normalization; its artifact is preserved, and the corrected rerun passed. No predictions, thresholds, or case selection changed between attempts.
