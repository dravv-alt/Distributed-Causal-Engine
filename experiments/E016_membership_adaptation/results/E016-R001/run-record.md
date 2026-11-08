# E016-R001 run record

- Planning reference: XP013.
- Run scope: 300 synthetic training scenarios; 300 held-out scenarios at membership sizes 8, 12, and 20; 100 eight-service ordering permutations; two malformed-input challenges.
- Models: fixed-eight MLP and shared per-service topology-feature MLP.
- Execution: local CPU; no network or remote compute; evaluator labels were not loaded by inference. `prediction-seal.json` hashes predictions before label evaluation.
- Result: see `evaluation.json` and `interpretation.md`.
- Independent audit: `independent-audit.json` passed.
- Failure record: no execution failure. The pre-existing permanent index discrepancy (`Next available ID: E004`) was retained; this experiment was registered additively in the dated E016 amendment.
- Scope limitation: synthetic architecture feasibility only; no RCAEval or real telemetry evaluation.
