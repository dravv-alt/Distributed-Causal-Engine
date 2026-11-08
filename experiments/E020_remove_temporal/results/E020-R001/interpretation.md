# E020-R001 interpretation — XP017

| Arm | Top-1 (95% Wilson CI) | Top-3 | MRR | Abstention | Coverage | Explanation coverage |
|---|---:|---:|---:|---:|---:|---:|
| Full fusion | 89.8% (87.2–92.0%) | 99.2% | 0.943 | 9.7% | 90.3% | 99.5% |
| Temporal disabled | 76.8% (73.3–80.0%) | 94.7% | 0.860 | 17.8% | 82.2% | 98.5% |

Temporal-disabled minus full paired Top-1 was -13.0 percentage points (95% bootstrap interval -15.8 to -10.3); paired MRR difference was -0.082 (interval -0.098 to -0.067). Earliest generated onset matched the synthetic root label in 81.3% of cases. The independent audit confirmed temporal-disabled scores were recomputed without using onset values.

The feature is an arbitrary generated number, without physical units, event-time semantics, clock-skew behavior, late arrival, missingness, or reset conditions. This does not validate temporal evidence on RCAEval or application telemetry.
