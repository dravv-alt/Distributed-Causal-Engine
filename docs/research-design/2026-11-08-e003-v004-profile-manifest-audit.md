# E003 V004 profile-to-manifest audit

Date: 2026-11-08
Type: Read-only reconciliation of saved local records
Status: Metadata reconciliation passed; source-byte verification unavailable in this checkout

## Question and method

Do the saved V004 profile JSON files map one-to-one to every telemetry CSV listed in the local OpenRCA manifest, with matching declared path metadata?

Ran `python docs/research-design/verify_e003_v004_profiles.py`. The script reads only `data/manifests/openrca.json` and saved V004 profile JSON files. It compares paths, expanded/compressed byte counts, headers, qualification markers, row-conservation markers, row-count field shape, and SHA-256 field shape. It does not open archives or rewrite results.

## Result

- Manifest telemetry CSV paths: 162
- V004 profile files: 162
- Matched paths checked: 162
- Missing or unexpected paths: 0
- Metadata errors: 0
- Outcome: `PASS_METADATA_RECONCILIATION`

This independently reproduces a bounded metadata/path reconciliation. It does not validate that the stored profile markers or hashes accurately describe the original bytes.

## Limits

`data/dataset/` in this checkout contains only the 13,469-byte manifest/index ZIP. The Bank, Market, and Telecom source ZIPs referenced by the manifest are absent. To preserve local-only operation, this audit did not download or access remote copies. It therefore did not recompute source CRCs, decompressed SHA-256 values, or row counts. The 162-file full-scan claim remains supported by the recorded V004 execution artifacts, but those source-byte properties were not independently re-established here.

This audit does not change E003's scientific decision. V006 still proposes REVISE / restricted downstream readiness pending human review; metric and trace semantics, two unassociated query rows, absent root observations in 50 cases, and absent root traces in 160 cases remain limitations. No successor experiment is authorized by this metadata check.
