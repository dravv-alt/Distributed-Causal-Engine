# V004 authorization record

User authorization: continue the unfinished E003 scientific audit in a new recorded run while preserving V002 as `77/162 PARTIAL`.

V004 follows V003's preflight block caused by an `EINVAL` read from Google Drive while hashing `Bank.zip`. V003 has zero inherited and zero completed profiles. V004 has no scientific-protocol change. It adds only bounded, resumable read retries for the G: streamed-file hash. A matching SHA-256 remains required before checkpoint reuse or audit execution.

Command:

`$env:PYTHONPATH='src'; .\.venv-e002\Scripts\python.exe -m dce_foundation.qualification.continuation_run --config experiments/E003_domain_model_adequacy/qualification/2026-10-04/continuation-V004/configuration.json --inherit-completed-from experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V002 --output experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V004`

New logs are `logs/V004-stdout.log` and `logs/V004-stderr.log`. Stop after report and independent validation for human review; do not start remediation, RCA reasoning, RCAEval, or data deletion.
