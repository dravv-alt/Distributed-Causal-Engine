# Preregistered hypothesis

Question: does dependency structure give useful exact-component localization information beyond matched non-graph references on the accepted E003 replay?

Hypothesis: a structural shared-dependency ranking can improve exploratory component localization. Improvement is not assumed and a negative result is useful. Lack of symptom evidence limits this to a topology prior, not an operational RCA diagnosis.

Independent variables: topology ranking, observation-volume reference, graph-disabled uniform reference; system/scenario.
Dependent variables: tie-aware Top-1/Top-3, deterministic Top-1/Top-3, candidate coverage, abstention, case-level differences, runtime and explanation evidence.
Controls: all 335 saved windows, exact opaque component identities, same candidate universe, no root-based case selection, no metric values/units/status/duration interpretation, no tuning, no future observations.
Dataset/version: E003-AM002 V006 Replay-1 inventory and canonical hashes, including referenced V004 artifacts; original dataset manifest inherited only.
Code version: source hashes/snapshot and Git commit/dirty status in preflight before execution.
Configuration: configuration.yaml, parsed as JSON-compatible YAML.
Random seeds: null; deterministic algorithms, no random sampling or bootstrap.
Hardware/environment: actual runtime recorded; standard-library-only Python with user-site disabled, no claim of a fully isolated virtualenv.
Repetitions: two independent rank computations on each input (second uses reversed iteration order), before evaluator access.
Results/failures/interpretation: generated under E004-R001; never presumed favorable.
Decision: technical gate separate from exploratory performance; human review required. No superiority conclusion from this experiment.
Next experiment: none authorized.
