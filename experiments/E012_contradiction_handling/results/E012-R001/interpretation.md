# E012-R001 interpretation

In the six frozen synthetic cases, support-only ranking selected three candidates and abstained once; two selections exactly matched the evaluator root. It made three false diagnoses. Contradiction-aware ranking rejected the contradicted candidate in all four cases containing contradiction evidence, selected two candidates, and abstained four times. It exactly matched the evaluator root in three cases and made no false diagnoses.

The observed trade-off is fewer false diagnoses and one more exact case, with three additional abstentions. With six constructed cases, this is logic behavior only; no statistical generalization or effectiveness claim follows. The fixture intentionally encodes the hypothesis-to-evidence relationship and cannot validate whether real telemetry deserves those evidence labels.

Implementation is an isolated experimental module and is not wired into the application’s RCA path. The first environment failure is retained. E012 does not qualify XP009 on real evidence.
