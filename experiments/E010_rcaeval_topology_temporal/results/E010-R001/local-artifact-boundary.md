# E010-R001 local artifact boundary

The 99,781-byte `predictions.jsonl` remains in the local result directory and is ignored by the repository's generated-prediction rule. It is not staged or pushed. The local artifact manifest and prediction seal identify it by SHA-256 `1772fed05eef5ffcbb5e463f467ce65c24bd8691a7093a4412f1dc9009f866f3`.

A remote checkout can verify the committed source and evaluation summary but cannot verify the saved prediction payload without the local file. Re-running requires the pinned RCAEval trace inputs and the E009 sealed baseline. No raw trace rows are committed in the evaluator summary.
