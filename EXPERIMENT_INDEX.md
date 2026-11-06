# Permanent experiment index

| ID | Question / purpose | State | Protocol | Execution / decision |
|---|---|---|---|---|
| E001 | Reproduce delivered R0 baseline and audit comparison semantics | Draft; not run under this ID | [hypothesis](experiments/E001/hypothesis.md), [configuration](experiments/E001/configuration.yaml) | [run](experiments/E001/run.md), [decision](experiments/E001/decision.md) |
| E002 | Investigate neural/SLO onset provenance and timing contribution | Reserved; blocked on E001 review | [hypothesis](experiments/E002/hypothesis.md), [configuration](experiments/E002/configuration.yaml) | [run](experiments/E002/run.md), [decision](experiments/E002/decision.md) |

| E003 | Domain model adequacy across OpenRCA systems/scenarios | R001 executed; downstream gate blocked, review required | [protocol](experiments/E003_domain_model_adequacy/protocol.md), [configuration](experiments/E003_domain_model_adequacy/configuration.yaml) | [run](experiments/E003_domain_model_adequacy/run.md), [decision](experiments/E003_domain_model_adequacy/decision.md) |

Next available ID: **E004**. _template is a template, not an experiment.
The delivered R0 baseline predates this register. It is external prior evidence, not an E001 result.

## ID and record policy

1. Allocate the next unused E-number in a reviewed index change. IDs, cancelled records and folder identities never change or disappear.
2. Copy [the template](experiments/_template/README.md), replace its ID, and register question, hypothesis and controls before substantial experiment code.
3. Draft protocols may be refined. Before execution, freeze the protocol/configuration in Git and record its commit, source snapshot, dataset hashes and environment.
4. Assign run IDs E001-R001, E001-R002, etc. Create a new run record and artifact paths for each run. run.md is the execution ledger; never overwrite earlier run entries/results.
5. Record code SHA plus dirty status. A SHA alone cannot identify untracked R0 source: record source-tree hashes and an archived snapshot, or commit it before a run.
6. Record actual configuration, dependency versions, seeds, hardware and exact commands. Mark unknown fields unknown; do not backfill invented values.
7. Preserve failure cases and unsuccessful runs. Separate observations, interpretation and decisions. Corrections are dated append-only amendments with author and reason.
8. A changed hypothesis/control/analysis after protocol freeze requires a new experiment ID; a rerun of an unchanged protocol gets a new run ID.
9. Promote results only after review of evidence, baseline independence, data leakage and uncertainty. Register the next experiment from that review.

Git supplies history and review, not physical write-once enforcement. Protected branches, review rules,
and immutable/versioned artifact storage should enforce this policy when repository hosting is configured.
Do not claim those controls are already installed.

## Required fields for every experiment

Question; Hypothesis; Independent variables; Dependent variables; Controls; Dataset/version;
Code version; Configuration; Random seeds; Hardware; Results; Failure cases; Interpretation;
Decision; Next experiment.

Small reviewed summaries, manifests, configurations and figures belong in Git. Large datasets/model weights
and unredacted logs belong in approved artifact storage; commit their URI, checksum, size and retention policy.
No sensitive telemetry should be published by an ignore exception.
