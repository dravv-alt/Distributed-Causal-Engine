# Execution ledger

E003-R001 is reserved for the initial bounded cross-system representation run. Execution evidence will record exact commands, source hashes, hardware, dependency versions, dataset hashes, limits and failures. No results are claimed at registration.

## E003-R001 — executed 2026-10-03

Registration above is retained as the pre-execution entry. The run is now executed, with an unsuccessful downstream-adequacy gate.

Commands, from repository root:

```powershell
$env:PYTHONPATH = 'src'
$env:PYTHONDONTWRITEBYTECODE = '1'
python -m dce_foundation.evaluation --inspect
python -m pytest -q -p no:cacheprovider tests
python -m dce_foundation.evaluation
```

The first pytest attempt additionally used `--basetemp .test-tmp-e003` inside the sandbox and failed on temporary-directory permissions. The successful test command ran with approved escalation; 39 tests passed, including four real-data integration samples. The failed scratch directory is ignored and retained; no recursive deletion was performed.

Run parameters: four scenarios; earliest/latest label selections; source-local day scope; 2,000-row cap per telemetry file; no random seed. Python 3.12, NetworkX 3.4.2, pytest 9.0.2. Platform/processor, actual Python build, Git HEAD/dirty status, dataset-manifest hash and source hashes are recorded in [run-manifest.json](results/E003-R001/run-manifest.json). RAM availability/peak utilization were not measured. Protocol/configuration were hashed, not committed or protected before execution: this is not a claimed immutable hosted freeze.

The [source snapshot](results/E003-R001/source-snapshot.zip) preserves the executed implementation/tests/configuration, with its SHA-256 in the manifest. Raw data is not inside that snapshot. Result hashes identify [adequacy.json](results/E003-R001/adequacy.json). Samples contain raw attributes and are ignored by Git; inspect locally under the result directory.

Outcome: eight deterministic repeated replays, 100,763 rows scanned, 98,736 mapped, 2,000 rejected, 27 outside the day scope. The Bank March 25 trace seconds/milliseconds inconsistency is preserved as a failure. No model/adapter patch was made to turn that result into success. Decision gate remains blocked pending review.

Read-only follow-up audit inspected the first trace row for all 29 trace files: Bank March 23–25 use seconds-scale values, unlike Bank March 4–12 and all inspected Market/Telecom first rows. This is first-row evidence, not a proof of uniform units within each entire file. The initial manifest does not include these later interpretation notes; documentation is a dated amendment, not a replacement run.

## Post-run implementation checks (not a new adequacy experiment)

- Code/test/protocol/configuration files still match R001 source hashes; snapshot entry hashes and result/snapshot SHA-256 match the run manifest.
- CLI `--incident Bank@135 --max-rows-per-file 50 --output data/processed/openrca/E003-cli-smoke` exited successfully and wrote five separate files: operational representation, ground truth, operational graph, evaluation graph and validation.
- JSON checks confirmed operational/evaluation separation and source-record conservation. A second invocation targeting the same directory raised FileExistsError; hashes of all five files remained unchanged.
- CLI `--incident Bank@134 --max-rows-per-file 1` produced explicit rejected-row evidence and a nonzero status, confirming failure is not hidden by a successful process exit.
- `git diff --check` passed; raw archives, serialized processed telemetry and raw sample JSONs are ignored. No Git commit or push occurred. E001/E002 files were not edited.

The CLI smoke output is local ignored processed data, not additional support for a full-incident adequacy claim. No model/adapter/validator changes were made after R001. Documentation amendments do not replace the frozen snapshot.
