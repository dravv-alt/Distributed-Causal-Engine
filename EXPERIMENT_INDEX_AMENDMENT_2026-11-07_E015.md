# Permanent register amendment: E015

Date: 2026-11-07 (Asia/Calcutta). Authority: user's explicit instruction to continue the campaign past pending review gates. This additive amendment registers E015 only; no existing register or experiment record is changed.

| ID | Purpose | Registered scope | Evidence |
|---|---|---|---|
| E015 | XP012 PyTorch–ONNX parity for E014 autoencoders | Export all nine frozen E014 CPU checkpoints with a locally available ONNX toolchain; compare PyTorch and ONNX Runtime outputs on normal, high-anomaly-score, missing-mask, and dynamic-batch inputs; report numerical/decision parity and CPU latency | `experiments/E015_onnx_parity/` |

Use local environment `tfpure` because it already contains ONNX 1.20.1 and ONNX Runtime 1.23.2; no installation or network access is required. This is a parity test of the E014 model artifacts, not an accuracy/quality evaluation. The permanent index's `Next available ID: E004` inconsistency remains visible.
