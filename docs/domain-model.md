# Domain model

Status: specification; implement and validate through registered experiments.

Environment contains service identities and instances. A topology snapshot states dependencies during a validity interval.
A telemetry observation has an event identity, event time, receipt time, metric kind, unit and quality.
A window contains synchronized raw observations, feature values and masks. Neural evidence and symbolic facts
support or contradict candidate root sets. A decision may identify anomalies, propose a causal hypothesis or abstain.
An incident aggregates related decisions with revisions. A plan recommends reviewed actions; feedback records operator assessment.

Identity is scoped by environment. A service name alone is not globally unique. Artifacts reference immutable
schema, topology, model, rule, fusion and configuration versions. Experiment/run IDs describe scientific provenance;
incident IDs describe runtime lifecycle. Do not use them interchangeably.
