# E002-R001 environment amendment — 2026-10-03

This amendment preserves E002-R001's original frozen configuration and result. It does **not** rewrite its environment after the fact or remove its compatibility warning.

## Historical fact

E002-R001 recorded Python 3.12.6, NumPy 2.5.3, scikit-learn 1.6.1, and NetworkX 3.4.2. Its run emitted a SciPy warning that NumPy 2.5.3 was outside SciPy's supported range. Hardware and a complete dependency lock were not frozen before the run. E002-R001 therefore remains `REVISE` pending review.

## Corrective control for a future run

`requirements-e002-lock.txt` is the controlled version set. `scripts/verify_e002_environment.py` creates an execution manifest that records interpreter, installed versions, hardware, thread settings, and the lock hash; it exits non-zero if versions differ.

The future runner must first verify its chosen interpreter explicitly, for example:

```powershell
python scripts\verify_e002_environment.py --output experiments/E002/environment/E002-R002-preflight.json
```

An isolated `.venv-e002` was created, but its package installation could not complete because package-index DNS access failed; it is not qualified and must not be used. The successful current-interpreter preflight is recorded separately at `experiments/E002/environment/E002-R002-preflight.json`.

Only a newly reviewed E002 run may use a qualified environment. This amendment does not authorize a rerun, change E002-R001, or unblock E003.
