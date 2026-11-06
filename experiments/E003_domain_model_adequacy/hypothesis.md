# Preregistered hypothesis

Question: Can a dataset-independent domain model preserve RCA-relevant OpenRCA evidence across Bank, Market/cloudbed-1, Market/cloudbed-2 and Telecom?

Hypothesis: Typed observations plus lossless source attributes, explicit event times, evidence-backed edges and isolated labels can represent each scenario without incident-specific branches. Unknown semantics and unresolved references may prevent downstream adequacy even when serialization succeeds.

Independent variables: system/scenario, source file schema, modality.

Dependent variables: source/mapped/rejected records; canonical observations; unknown units; missing values; duplicates; parent resolution; labels observed in telemetry; timestamp/date consistency; deterministic digest.

Controls: fixed adapter/model version, deterministic selection and ordering, no root-cause inference, no unit inference from names, raw files read-only, labels isolated.

Dataset/version: local OpenRCA ZIP archives; upstream commit UNKNOWN; inventory and SHA-256 in data/manifests/openrca.json.

Code version: run-manifest source-file hashes plus Git HEAD and dirty status; source snapshot identifies uncommitted implementation.

Configuration: configuration.yaml and recorded exact command.

Random seeds: none; deterministic selection, no sampling randomness.

Hardware: recorded at execution.

Results: see results; not presumed successful.

Failure cases: unknown units, aliases, missing parents, invalid timestamps/values, unsupported fields, incomplete scan.

Interpretation: parsing is necessary but not sufficient for downstream RCA.

Decision: see decision.md; human review required.

Next experiment: not authorized pending E003 review.
