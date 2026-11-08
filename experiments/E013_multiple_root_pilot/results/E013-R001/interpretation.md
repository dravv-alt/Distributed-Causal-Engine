# E013-R001 interpretation

| Method | Exact root sets | Multi-root collapse | Ambiguous outputs | Empty sets | Mean output size |
|---|---:|---:|---:|---:|---:|
| Unique single-root baseline | 2/6 (33.3%) | 3/3 (100%) | 0/6 | 3/6 | 0.50 |
| Root-set threshold 2 | 4/6 (66.7%) | 1/3 (33.3%) | 3/6 | 0/6 | 1.50 |

The fixed root-set method represented multiple roots more often on this designed fixture. It also emitted multiple roots in one of three single-root controls. Its threshold is a frozen synthetic setting, not a calibrated operational value. The cases were deliberately constructed and are too few for generalization or statistical inference.

This shows that the experimental module can preserve a set of candidate roots under explicit support facts. It does not show that DCE can identify simultaneous faults from RCAEval or service telemetry, and it is not integrated into the application inference path.
