# E015-R001 interpretation

## Numerical and decision parity

All nine E014 model checkpoints exported and passed ONNX checker validation. On normal-prefix, maximum robust-z, maximum-missingness, and batch-16 inputs, every PyTorch/ONNX Runtime output pair satisfied `allclose(atol=1e-5, rtol=1e-4)`. All frozen E014 threshold decisions matched exactly.

Across tested inputs, maximum absolute output difference was `2.86e-6`. Maximum relative difference was `0.00673`; this occurred for values near zero, while the absolute tolerance and combined `allclose` check passed. Dynamic batch dimensions worked at batch sizes 1 and 16. Eight of nine cases supplied a selected row with at least one missing feature; the remaining case had no missing metrics in any row.

## CPU latency

Median of per-model median latencies (100 measurements after 10 warmups) was:

| Batch | PyTorch CPU | ONNX Runtime CPU |
|---|---:|---:|
| 1 | 0.229 ms | 0.058 ms |
| 16 | 0.252 ms | 0.086 ms |

These are small local microbenchmarks on the current Windows machine, using PyTorch 2.10 CPU and ONNX Runtime 1.23.2. They include Python call overhead and are descriptive; they do not establish service-level performance.

## Limits

Export used the same stored E014 weights, loaded in PyTorch 2.10.0+cpu, while E014 training used PyTorch 2.4.0+cu124 on CPU. Parity is between PyTorch 2.10 and ONNX Runtime for those weights, not a cross-version training reproduction. The tests cover one local model per selected case and the E014 preprocessing/thresholds; they do not evaluate accuracy, generalization, training reproducibility, or application integration. The missing-mask case for one dataset had no actual missing values.
