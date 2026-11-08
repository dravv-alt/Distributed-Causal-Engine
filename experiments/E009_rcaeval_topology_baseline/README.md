# E009 — RCAEval topology-only localization baseline

Planning alignment: XP006. This additive experiment continues the campaign under the user's instruction to proceed through pending review gates. E009 is a new permanent identity; it does not claim that XP001–XP005 passed.

The baseline builds caller-to-callee service edges from parent-span references in the nine staged blind RCAEval cases. It ranks observed services by the number of distinct other services that reach them. Prediction code reads only trace Parquet files in blind inference directories; it does not read labels, case names, metrics, logs, the evaluator index, or the sample-selection mapping. Labels are joined by a separate evaluator only after the prediction file hash is sealed.

The local sample is small and deliberately selected. This is a descriptive topology-only baseline, not an online detector, causal method, or neuro-symbolic comparison.
