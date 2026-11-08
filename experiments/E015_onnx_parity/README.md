# E015 — PyTorch and ONNX Runtime parity

Planning alignment: XP012. This experiment consumes the nine saved CPU autoencoder weights from E014 and exports them locally to ONNX. It compares the same weights and preprocessed inputs in PyTorch and ONNX Runtime. Inputs cover a fit-prefix row, a highest robust-z row selected without labels, a row with the most missing features, and a dynamic batch of 16.

Run using the already installed local `tfpure` environment:

```powershell
& 'C:\Users\bhavv\anaconda3\envs\tfpure\python.exe' experiments/E015_onnx_parity/scripts/run_parity.py
& 'C:\Users\bhavv\anaconda3\envs\tfpure\python.exe' experiments/E015_onnx_parity/scripts/independent_audit.py
```

No dependencies are installed and no network or remote compute is used. This experiment measures runtime parity, not anomaly-detection effectiveness.
