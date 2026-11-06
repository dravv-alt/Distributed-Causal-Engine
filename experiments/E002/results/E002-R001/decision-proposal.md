# E002-R001 decision proposal

**Review status:** pending human review. This is a new run artifact; existing E002 records are unchanged.

## Proposed decision: REVISE

E002-R001 passes its deterministic repeatability and source-policy integrity gates. It does not pass the preregistered superiority gate: paired Top-1 difference is 0.000 with a 95% CI of `[0.000, 0.000]` across 237 events. No hybrid, timing, or provenance-superiority claim is justified.

The run also has a protocol-environment qualification failure: dependency versions and hardware were not frozen before execution, and the active NumPy/SciPy combination warned of incompatibility. This makes the performance result exploratory despite exact repetition within that active environment.

## Required revision before any repeat

1. Create a separately reviewed experiment/run configuration that pins Python, NumPy, SciPy, scikit-learn, NetworkX, OS/hardware, thread settings, and a dependency lock hash before execution.
2. Resolve the incompatible NumPy/SciPy environment rather than suppressing its warning.
3. Keep the three E002-R001 policies and seed sets intact if repeating this protocol; a changed treatment, metric, seed set, topology, or analysis requires newly reviewed scope under the register policy.
4. Do not begin E003 remediation or downstream RCA work from E002-R001.

**Next permitted action:** human review of this proposal. No automatic successor is authorized.

