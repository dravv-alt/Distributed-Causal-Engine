# E002 controlled environment

## Current qualification

`E002-R002-preflight.json` records a passing environment verification on 2026-10-03:

- Python 3.12.6 at `C:\Python312\python.exe`
- NumPy 1.26.4, SciPy 1.15.1, scikit-learn 1.6.1, NetworkX 3.4.2
- 20 logical CPUs, 23.78 GiB physical memory
- thread-limit variables unset
- lock-file SHA-256 `694071fa9d6850d9cab412f1c135879427f5846a166eec7fc7d6e411f1309320`

The preflight is a controlled environment record for a **future** E002 rerun. It does not retroactively qualify E002-R001, whose environment warning remains part of its evidence.

## How to verify before a newly authorized run

```powershell
$env:PYTHONPATH = 'dce-r0\dce\src'
python scripts\verify_e002_environment.py --output experiments/E002/environment/<new-run>-preflight.json
```

Use the run only if `qualified` is `true`. Record the preflight JSON hash in that new run's artifact manifest. A changed lock file, interpreter, package version, thread setting, dataset, seed set, or evaluation policy requires review before execution.

## Isolated environment status

`.venv-e002` is unqualified: it was created but dependency installation could not finish because DNS access to package indexes failed. Do not use it until dependencies install and the verifier passes. The pinned lock file remains the intended installation specification.

## 2026-10-03 remediation update

The original partial virtual environment was discarded. A new `.venv-e002` was created with `--system-site-packages` after package-index installation again failed with DNS errors. It inherits the exact, locally installed versions from the verified `C:\Python312` environment. This offline provenance is recorded in [the qualified R002 preflight](E002-R002-preflight-qualified-2026-10-03.json), which passed every verifier check.

This is an environment qualification only. It does not alter E002-R001 or constitute an E002-R002 result.
