# V005 recovery authorization and lineage

User authorized a controlled full recovery workflow after read-only audit of V004. V004 is immutable historical evidence: `162/162` profiles, `164` valid Replay-1 artifacts, `1` corrupt Replay-1 artifact, `170` missing Replay-1 artifacts, no Replay 2 and no finalization.

V005 parent: `V004`.

Recovery reason: `V004 interrupted during Replay 1 before completion.`

Frozen lineage: `inherited_profiles=162`; `expected_replay1_windows=335`; `inherited_valid_replay1=164`; `corrupt_replay1=1`; `missing_replay1=170`; `replay1_to_reconstruct=171`; `inherited_v002_profiles=77`.

Command: `$env:PYTHONPATH='src'; .\.venv-e002\Scripts\python.exe -m dce_foundation.qualification.recovery_run --config experiments/E003_domain_model_adequacy/qualification/2026-10-04/continuation-V005/configuration.json --output experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V005`.

V005 must stop after final technical artifacts and independent audit. It cannot declare E003 scientifically passed or advance downstream work.
