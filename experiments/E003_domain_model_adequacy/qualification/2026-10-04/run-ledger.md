# Append-only execution ledger

## V001 — full census with individual compressed rows

Command: `.venv-e002/Scripts/python.exe -m dce_foundation.qualification.run --config experiments/E003_domain_model_adequacy/qualification/2026-10-04/configuration.json --output experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V001` with `PYTHONPATH=src`.

Eleven CSV profiles completed through EOF. The run was intentionally interrupted during the next Bank trace file after storage overhead was observed. No overall scientific gate result was produced. Partial context, profiles, source snapshot, provenance and stdout/stderr remain preserved. The interrupted file is not inherited as complete.

## V002 — lossless compressed-block continuation

Command: `.venv-e002/Scripts/python.exe -m dce_foundation.qualification.compact_run --config experiments/E003_domain_model_adequacy/qualification/2026-10-04/configuration.json --inherit-completed-from experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V001 --output experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V002` with `PYTHONPATH=src`.

stdout: `logs/V002-stdout.log`; stderr: `logs/V002-stderr.log`.

The physical storage revision is described in `storage-amendment.md`. It retains exact selected field strings and unchanged temporal selection rules. Completed profiles are reused only with a transfer manifest and row-count checks. The unfinished file is scanned again from its beginning. The new implementation and configuration are frozen in the V002 source snapshot before its execution. No existing experiment record was overwritten.

Final completion/failure and gate evidence will be written as separate new records after execution; this entry does not claim that V002 has finished.
