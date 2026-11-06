# E003-AM002 V003 continuation authorization and freeze

User explicitly authorized continuing unfinished scientific work in a new recorded run while preserving V002 as 77/162 partial. Latest location clarification identifies `G:/My Drive/DCE/data/dataset`. Cloud reupload/storage verification is separate; this is not permission to delete any source or advance to RCAEval.

Scientific question, A-H gates, annotation windows, UNKNOWN semantics, evaluator isolation, seeds (null) and two projected replays remain the AM002 protocol. V003 changes only checkpoint import and dataset location. Existing executed source and records remain unchanged. Its source/configuration snapshot is captured before execution. The original safety limits remain 6 GiB minimum free and 6 GiB maximum context store; an additional per-case replay guard uses the same free-space floor.

Before inheriting: verify every V002 file against the recorded source inventory, validate all dataset archive SHA-256 values against the original dataset manifest, and check completed-file EOF/CRC, catalog and selected-row conservation. Import only blocks whose source has a complete profile. Discard no originals; omit incomplete-file blocks from the new database and rescan that entire source file. Preserve the inherited V001 chain in V002 unchanged.

Command with `PYTHONPATH=src`: `.venv-e002/Scripts/python.exe -m dce_foundation.qualification.continuation_run --config experiments/E003_domain_model_adequacy/qualification/2026-10-04/continuation-V003/configuration.json --inherit-completed-from experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V002 --output experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V003`.

New logs: `logs/V003-stdout.log`, `logs/V003-stderr.log`. Results: `results/V003`. No V003 outcome is presumed. Stop for report/independent verification/human review. V002 remains historically PARTIAL even if V003 later completes.
