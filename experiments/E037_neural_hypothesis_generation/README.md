# E037 / XP034 neural hypothesis generation pilot

Synthetic CPU pilot: a small PyTorch model proposes one of DB, network, or cache hypotheses from generated metric/topology/time features. A separate symbolic verifier checks candidate-specific support and abstains otherwise. This is not real workload evidence or a DCE application integration.
