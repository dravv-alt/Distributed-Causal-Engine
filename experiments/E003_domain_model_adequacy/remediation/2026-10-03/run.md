# E003-AM001 execution record

Authorization: the user's Real-World RCA Transition attachment and `Proceed` instruction, 2026-10-03. Periodic scope rereading requested by user and applied at model, test, corpus and final gate checkpoints. No permanent ID allocation.

## Frozen controls

Protocol and configuration.json were created before substantial v2 implementation. Up to 512 first logical records from every telemetry file; complete record/query annotations; complete deployment workbook. Four scenarios, fixed UTC+08 day interpretation and one-hour profiling allowance, fixed >=99% unique-scale support, two passes, no random seeds. Raw sources are read-only. No post-result protocol/selection/gate changes.

## Exact commands

```powershell
& .\.venv-e002\Scripts\python.exe -m pytest -q -p no:cacheprovider tests\test_representation_v2.py
$env:PYTHONPATH = 'src'
& .\.venv-e002\Scripts\python.exe -m dce_foundation.representation_v2.audit --config experiments\E003_domain_model_adequacy\remediation\2026-10-03\configuration.json --output experiments\E003_domain_model_adequacy\remediation\2026-10-03\results\V001
& .\.venv-e002\Scripts\python.exe -m dce_foundation.representation_v2.audit --config experiments\E003_domain_model_adequacy\remediation\2026-10-03\configuration.json --output experiments\E003_domain_model_adequacy\remediation\2026-10-03\results\V002
& .\.venv-e002\Scripts\python.exe -m dce_foundation.representation_v2.audit --config experiments\E003_domain_model_adequacy\remediation\2026-10-03\configuration.json --output experiments\E003_domain_model_adequacy\remediation\2026-10-03\results\V003
& .\.venv-e002\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
& .\.venv-e002\Scripts\python.exe scripts\check_project_governance.py
git diff --check
```

Each audit's stdout/stderr is retained under logs/V00N-*.log. Preflight includes actual source hashes/snapshot, interpreter, dependency versions, Git SHA and dirty status. configuration.json's original V001 intention is historical; output directory/summary identifies each actual attempt. No old output directory was overwritten.

V001: failed engineering attempt; SQLite resource identity column absent. V002: completed twice; raw results retained; later workbook kind overwrite identified. V003: corrected workbook typing validated with fixtures and repeated corpus processing. Tests: initial 24 pass/1 failure/1 setup error; corrected new suite 27 passed; final full suite 76 passed. Failures and corrections documented separately.

Git status capture emitted Windows permission warnings for pre-existing pytest cache directories. These are retained in stderr; they did not prevent source snapshots or corpus processing. Test temp-directory access required sandbox escalation. No package installation, commit, push, raw archive write, RCAEval download or RCA reasoning occurred.

Detailed current interpretation is report.md and decision.md; actual machine-readable outputs are results/V003. Do not reinterpret an audit process exit of zero as adequacy approval.
