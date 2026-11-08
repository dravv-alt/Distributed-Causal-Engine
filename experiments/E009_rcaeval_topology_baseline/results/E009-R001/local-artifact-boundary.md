# E009-R001 local artifact boundary

`predictions.jsonl` is present in the local run directory and is referenced by the prediction seal and final artifact manifest. It matches the repository's ignore rule for generated JSONL/prediction payloads, so this file is intentionally not included in the Git commits or pushed to the remote.

- Local artifact: `experiments/E009_rcaeval_topology_baseline/results/E009-R001/predictions.jsonl`
- Rows: 9
- Bytes: 4,112,980
- SHA-256: `36ec3964ce888b50001a70a3f02c23d33d81e4c5a7d0fa3ea62395795e5a9545`

The local artifact-manifest verification covers this file. A remote checkout alone cannot verify that entry or reproduce the saved-prediction audit without the local payload; it can reproduce the run from the pinned local RCAEval inputs and committed code. No raw trace rows are included in the committed evaluator report.
