# E010 execution ledger

E010-R001 predictions were generated for all nine frozen blind cases. The run verified unchanged E009 trace inputs and topology predictions, sealed predictions before label access, independently audited the label-blind results, then evaluated exact service labels. Commands ran from the repository root:

```powershell
python experiments/E010_rcaeval_topology_temporal/scripts/run_predictions.py
python experiments/E010_rcaeval_topology_temporal/scripts/independent_audit.py
python experiments/E010_rcaeval_topology_temporal/scripts/evaluate_labels.py
python experiments/E010_rcaeval_topology_temporal/scripts/independent_evaluation_audit.py
```

See `results/E010-R001/` for outputs, source snapshot, input hashes, label-free prediction seal, evaluator hashes, and artifact manifest. Execution was standalone/local because OpenResearch is unavailable.
