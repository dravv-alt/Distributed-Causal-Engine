# E002-R001 and E002-R002 comparison

R002 is a clean-environment rerun, not a new experimental variant. E002-R001 remains unchanged.

| Item | E002-R001 | E002-R002 | Comparison |
|---|---|---|---|
| Runner SHA-256 | `aa3500836bbbd3b43d58b557b2b66019e5f68e20d9a2c098a1f38e6723a5e696` | same | Same implementation |
| Raw-result SHA-256 | `592171d8dbaa7ce57934ec546d74b0d7fb733109b4f2ab7c24e27c1c9d49269f` | same | Byte-identical raw results |
| Repetition hashes | all `75dac…5c58` | all `75dac…5c58` | Exact match |
| Paired Top-1 difference | `0.000`, CI `[0.000, 0.000]`, n=237 | same | Exact match |
| Mixed / same-source cross-source pairs used | 306 / 0 | 306 / 0 | Exact match |
| Environment qualification | failed / incomplete | passed before and after execution | R002 resolves the recorded environment issue |
| Raw `summary.json` SHA-256 | `39f199…00f3` | `a15fa8…19ad` | Expected difference: summary embeds the resolved configuration hash |

The two raw-results files are byte-identical. The summaries differ only because each records the hash of its own configuration file; R002's resolved configuration includes the required R002 execution-context provenance.

## Important limitation

R002 used a freshly created virtual environment with `--system-site-packages` after the package index could not be reached due to DNS failure. The environment verifier confirmed the active interpreter and every locked version. This is sufficient for this host's qualified rerun, but it is not a wheel-hash-backed installation record that another machine can recreate without access to equivalent package artifacts.

