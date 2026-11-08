# E015-R001 protocol — frozen before parity execution

**Date:** 2026-11-07 (Asia/Calcutta). **Planning alignment:** XP012 / RQ3. **Scope:** all nine E014-R001 CPU autoencoder checkpoints.

## Frozen inputs and preprocessing

Use each E014 model checkpoint and its E014 `neural_threshold`. Recreate E014's numeric feature selection and robust preprocessing from the corresponding blind metric Parquet: first 35% rows provide fit median/MAD; all-null medians fall back to 0; zero/nonfinite scales fall back to 1; standardized values are clipped to [-10, 10]; append per-feature missingness masks. No evaluator labels, injection times, root-cause fields, or fault schedule are read.

For each case, construct inputs without labels: `normal` = first fit row; `high_score` = row with maximum robust max-absolute-z score across the full metrics file; `missing_mask` = row with greatest count of missing features; `boundary_batch` = 16 copies of the normal input. Test each single-row input and the dynamic batch. The model input width is twice the case feature count, so the nine cases also cover different fixed input widths.

## Export and comparisons

- Toolchain: local Python 3.10.18, PyTorch 2.10.0+cpu, ONNX 1.20.1, ONNX Runtime 1.23.2; CPU only; legacy `torch.onnx.export`, opset 17, dynamic batch axis.
- Compare PyTorch and ONNX Runtime output arrays for every input. Require `numpy.allclose(atol=1e-5, rtol=1e-4)` and exact equality of reconstruction-MSE threshold decisions against the frozen E014 threshold.
- Report maximum absolute and relative error, decision matches, model load/export status, and CPU latency medians after warm-up for batch sizes 1 and 16. Latency has no pass threshold.
- Validate each ONNX file with `onnx.checker` before ORT evaluation.

## Provenance and limits

E014 weights, E014 prediction seal, model thresholds, and telemetry hashes are the source inputs. Record all hashes and actual environment. This parity test does not evaluate accuracy, model quality, missingness robustness, or generalization. No random seed is used; export and inference are deterministic. All artifacts and data remain local; no network or remote execution.
