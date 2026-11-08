# Hypothesis

The E014 PyTorch autoencoder checkpoints can be exported with the local ONNX exporter and produce numerically close CPU outputs in ONNX Runtime for normal, high-score, missing-mask, and dynamic-batch inputs. Given the same E014 threshold, both runtimes should produce identical binary anomaly decisions on the frozen inputs.

The experiment does not test whether the model or threshold detects real anomalies effectively.
