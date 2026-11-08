# E015 execution ledger

## E015-R001

The run verified E014 prediction and artifact hashes, loaded all nine saved checkpoints, exported them with the locally installed `tfpure` environment, checked each ONNX file, and compared PyTorch CPU output with ONNX Runtime CPU output. No label or evaluator index was read.

Commands:

```powershell
& 'C:\Users\bhavv\anaconda3\envs\tfpure\python.exe' experiments/E015_onnx_parity/scripts/run_parity.py
& 'C:\Users\bhavv\anaconda3\envs\tfpure\python.exe' experiments/E015_onnx_parity/scripts/independent_audit.py
```

All nine exports passed; the independent audit reproduced the input suite, verified ONNX models and CPU providers, and confirmed the sealed parity report. Export emitted PyTorch's legacy-exporter deprecation warning. NumPy emitted all-NaN-slice warnings for features with no training-prefix values; median and scale fallbacks matched the E014 preprocessing contract.
