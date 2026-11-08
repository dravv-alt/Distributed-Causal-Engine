# E015-R001 provenance review — 2026-11-08

This additive review records local integrity checks. It does not change the parity output or proposed decision.

## Integrity checks

- All 14 files listed in the E015 artifact manifest exist and match recorded byte counts and SHA-256 hashes.
- All 9 E015 source-file hashes and all 9 telemetry hashes in `provenance.json` match the local files.
- All 9 E014 checkpoint hashes referenced by E015 match the local checkpoint files.
- `parity.json` matches its prediction-free parity seal; the saved independent audit reports PASS for all nine cases.

## Reproducibility and privacy boundary

The provenance records content hashes and tool versions, but no Git commit or dirty-tree state. The E015 source files are currently untracked, so the retained evidence cannot establish a Git-frozen pre-run snapshot. Telemetry and generated model/parity artifacts remain local and are not added to Git. The committed Markdown records describe the result without publishing those files.

## Interpretation boundary

The observed result is numerical and threshold-decision parity for the nine tested E014 checkpoints and the frozen input shapes/tolerances. It does not qualify detector accuracy, cross-version training reproduction, production latency, or application integration. The existing proposed disposition remains `PROCEED` only within this parity scope; human review remains pending.
