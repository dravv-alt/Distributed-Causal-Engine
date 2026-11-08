# E036-R001 protocol (2026-11-07)

Planning reference XP033. User authorization: proceed past pending gates, documented additively. Train a PyTorch bag-of-token classifier on 300 generated messages (100 each: connection-pool exhaustion, timeout, healthy). Evaluate on 150 separately generated held-out messages (50 per class); seed 36033. Compare with a fixed keyword baseline. Inference receives only text plus provenance fields; test labels stay in evaluator-only data until evaluation. Report event accuracy, macro F1, output-schema compliance, provenance retention, and model/runtime facts. Confidence is softmax score and is not claimed calibrated.

No approved acceptance threshold exists. The synthetic set is a pipeline pilot only. An available RCAEval log sample can be read for schema/inference smoke, but its unlabeled predictions are not scored or used for training. No case-level evaluator labels are read by the model.
