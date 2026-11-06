# E002-R001 derived metrics

## Predefined gates

| Gate | Result | Evidence |
|---|---|---|
| Exact repeatability | PASS | Three full end-to-end repetitions produced the identical canonical metrics SHA-256: `75dac86f78573fac799f0e90103ba2501bf44e6863afe47d7f7117f7bc5f5c58`. |
| Treatment integrity | PASS | Same-source-only used 0 cross-source timing pairs; mixed-current used 306 across the five held-out seeds. Candidate detection and thresholds were fixed. |
| Superiority | FAIL | Paired same-source-only minus mixed-current Top-1 = 0.000; 95% paired bootstrap CI `[0.000, 0.000]`, n=237. The preregistered +0.050 and CI requirement is not met. |
| Protocol/environment qualification | FAIL | Dependency versions and hardware were not frozen before execution; the actual environment emitted a NumPy/SciPy compatibility warning. |

The frozen runner's mechanical `overall_gate` is true because it intentionally combines only repeatability and treatment integrity. It does **not** override the separate superiority and protocol/environment failures above.

## Held-out performance

| Seed | Events | Mixed Top-1 | Same-source Top-1 | Timing-disabled Top-1 | Same-source − mixed |
|---:|---:|---:|---:|---:|---:|
| 31 | 53 | 0.849 | 0.849 | 0.792 | 0.000 |
| 32 | 41 | 0.902 | 0.902 | 0.902 | 0.000 |
| 33 | 54 | 0.815 | 0.815 | 0.815 | 0.000 |
| 34 | 44 | 0.841 | 0.841 | 0.864 | 0.000 |
| 35 | 45 | 0.956 | 0.956 | 0.978 | 0.000 |

All treatments had event recall 1.0, incident precision 1.0, and 0 false positives across these five synthetic held-out datasets. This is an easy simulator regime and does not support an operational false-alert claim.

## Interpretation

The provenance control works mechanically: 306 cross-source pairs were observable under the mixed policy and none was used in same-source-only. But in this simulator and frozen configuration, removing those pairs changed no event-level Top-1 decisions. E002-R001 therefore provides repeatability and policy-integrity evidence, **not** evidence that provenance consistency improves root ranking.

The timing-disabled control sometimes equalled or exceeded timing-enabled policies (seeds 34 and 35). This is an observation requiring a later, separately authorized hypothesis; it is not a post-hoc reason to tune E002.

