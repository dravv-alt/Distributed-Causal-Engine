# E016-R001 interpretation — XP013

## Outcome

The synthetic architecture pilot supports the narrow software-design claim that a shared per-service scorer can accept variable membership and preserve service identity under reordering. It does not establish RCA quality on RCAEval, DCE telemetry, or real distributed systems.

| Services | Fixed-eight Top-1 (95% Wilson CI) | Shared-topology Top-1 (95% Wilson CI) | Shared Top-3 | Shared MRR |
|---:|---:|---:|---:|---:|
| 8 | 98% (93.0–99.4%) | 98% (93.0–99.4%) | 99% | 0.988 |
| 12 | Rejected 100/100 | 98% (93.0–99.4%) | 100% | 0.990 |
| 20 | Rejected 100/100 | 96% (90.2–98.4%) | 100% | 0.978 |

The shared model accepted all 300 valid held-out cases. It returned identical service rankings for all 100 service-order permutations; maximum score change was 1.91e-6. The fixed-size model rejected all 100 reordered inputs. The shared input validator rejected both malformed challenges (duplicate service ID and dangling edge).

## Interpretation limits

- This is a synthetic generator with one root and deliberately shifted signals; it has no calibrated units or real telemetry semantics.
- The held-out cases share the same generator and service-ID conventions as training. These intervals describe the generated cases only.
- The fixed model is deliberately order-sensitive and contract-bound; its rejection is a mismatch-safety behavior, not a quality score.
- The dynamic model's strong localization is not evidence that topology helps: at eight services it ties the baseline, and this design does not isolate topology's causal contribution.
- The run does not answer the campaign's main held-out RCAEval comparison or prove adaptation to unseen real service names, schemas, graph patterns, or fault mechanisms.

## Record

Independent recomputation passed for Top-1, Top-3, MRR, mismatch counts, permutation behavior, malformed-input rejection, and the prediction seal. Result classification: **synthetic feasibility evidence; real-data effectiveness remains UNKNOWN**. Next campaign activity is XP014 (fusion ablation) only within the current user-directed campaign authorization; do not reuse these synthetic scores as RCAEval or service-set effectiveness evidence.

Artifacts and hashes are listed in `artifact-manifest.json`.
