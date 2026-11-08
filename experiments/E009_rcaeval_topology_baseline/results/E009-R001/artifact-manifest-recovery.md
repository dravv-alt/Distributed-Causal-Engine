# E009-R001 artifact-manifest recovery

The initial `artifact-manifest.json` is preserved but invalid JSON because its generator appended a literal `\\n` after the object. This affected only the final packaging manifest; predictions, the prediction seal, graph audit, evaluation, and metric audit were already written. The failure is recorded in `artifact-manifest-attempt-001-failure.json`.

`artifact-manifest-v2.json` is the corrected JSON inventory. It includes hashes for the first manifest and its failure record as well as all other run artifacts, excluding itself. Verify it before consuming the run package.
