# E001-R001 decision proposal

**Review status:** pending human review. This is a new run artifact; it does not modify the protected E001 decision record.

**Evidence:** E001-R001 completed with CLI exit status 0. Its five comparable result tables have zero mismatches against the delivered R0 report after path normalization. See [execution record](../../logs/E001-R001.md) and [artifact manifest](artifact-manifest.json).

**Results and uncertainty:** The delivered synthetic result is reproducible once on this Windows host from the locally pinned archive. It is not a repeated-run, independent-host, real-telemetry, calibrated, or production result. The hybrid does not show a stable +5pp Top-1 advantage over the strongest ablation; observed paired gains range from -0.021 to +0.032.

**Failure cases:** R0's test suite is not clean (25 passed, 1 code-level failure, 2 pytest ACL errors). The reproduction CLI nevertheless executed its save/load production path successfully. Hardware could not be queried in the sandbox.

**Proposed decision:** **REVISE**. Preserve E001-R001 as baseline-reproduction evidence. Before E001 can be treated as a clean gate, repair or explicitly scope the in-memory bundle test defect, obtain a clean test environment, and preregister acceptance tolerances/repeat-run criteria. Do not claim hybrid superiority from this result.

**Proposed next scope after review:** E002 may assess onset/timing provenance only after reviewer approval and a frozen protocol. E003 retains its separate blocked decision; E001-R001 does not override it.
