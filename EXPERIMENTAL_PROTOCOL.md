# DCE experimental constitution — v1

Adopted by user instruction on 2026-10-03. Authoritative source: [archived execution program](docs/governance/EXECUTION_PROGRAM_ORIGINAL.md). This document structures its rules; it does not replace the permanent experiment register, create new experiments, approve gates or retroactively qualify existing runs.

## Purpose and research model

DCE is a research project in which the application is the experimental instrument. Investigate whether explicit representations of distributed structure, time, evidence, mechanisms and constraints improve localization/remediation over statistical/neural evidence alone. Maintain three linked tracks: system building, experiments and documentation. Every architectural component must trace to a research question, hypothesis, controlled test, evidence and reviewed decision.

## Fifteen laboratory rules

1. No architectural claim without an experiment.
2. No experiment without a hypothesis.
3. No result without an explicit baseline/reference. For representation tests this can be the source records/schema or a reconstruction oracle; predictive comparisons need independent competing baselines.
4. No comparison without controlled variables.
5. Every model has a version, including symbolic rules, schema/ontology, preprocessing and fusion contracts.
6. Every dataset has a manifest and provenance.
7. Every run records resolved configuration and seeds; deterministic no-randomness runs record `null` with justification.
8. Every result has raw artifacts or controlled artifact references/checksums; do not publish sensitive telemetry to satisfy this rule.
9. Every failure is documented, including environment failures and rejected source records.
10. Every major architecture change gets a decision record tied to evidence.
11. Ablations are mandatory for claimed component contributions; disabled branches must actually be independent.
12. Causal claims require documented assumptions, identification limits and intervention evidence. Observations and causal hypotheses are not established causality.
13. Self-healing claims require controlled execution, safety constraints, verification and failure/rollback evidence.
14. Performance claims require a defined workload, hardware, environment, versions and measurement procedure.
15. Reproducibility is an explicit evaluation criterion, not a claim based on parser or unit-test success.

## Experiment identity and evidence chain

The permanent register is [EXPERIMENT_INDEX.md](EXPERIMENT_INDEX.md). E001/E002/E003 retain their existing meanings. Source-program E-labels are historical planning labels, not allocations; use the XP-stage mapping to recover their intent. The next available E-number is not permission to allocate it.

Every experiment records: Question; Hypothesis; Independent variables; Dependent variables; Controls; Dataset/version; Code version; Configuration; Random seeds; Hardware; Results; Failure cases; Interpretation; Decision; Next experiment. Add a protocol, deterministic run IDs, artifacts/manifests, acceptance thresholds and a review record. Distinguish source rows, canonical observations, selected incidents and population coverage.

Trace: research question → hypothesis → design → dataset → code → configuration → run → raw results → analysis → figures/tables → failures → decision → justified architecture change → authorized next experiment. Commit identity alone does not identify dirty/untracked source: retain source hashes/snapshot. Do not assert protected/immutable hosting controls exist when only local files and Git are available.

## Standard decision outcomes and review

| Outcome | Meaning | Permitted next step after review |
|---|---|---|
| PROCEED | Evidence supports the approach within stated scope | Only the explicitly approved successor scope |
| REVISE | Model/implementation is insufficient but promising | Reviewed revision plan; preserve original failed evidence |
| REPEAT | Contamination or inadequate control prevents interpretation | Preregister corrected controls and a non-overwriting run |
| BRANCH | Competing approaches merit controlled comparison | Allocate reviewed branch experiments independently |
| ABANDON | Evidence does not justify the complexity | Preserve negative result and remove only with authorized changes |

Review status is separate from outcome: pending, approved, rejected. A recommendation such as REVISE is not human approval. Do not invent statistical significance, thresholds, reviewer names or dates. Decision records include experiment/question, results/uncertainty, statistical analysis where applicable, observed failures, interpretation, outcome, reason, permitted next scope, reviewer and date.

On failure distinguish **model inadequacy**, **engineering defect**, **source-data ambiguity**, **coverage limitation**, and **environment/experimental contamination**. Diagnose before changing anything. An unchanged frozen protocol rerun gets a new run ID; a changed hypothesis/control/analysis gets a new experiment ID under the register. With current no-record-edit authority, present proposals in new amendment files and request permission for the registration/source changes they require.

## Gate discipline

No automatic E-number/phase progression. Read the actual predecessor decision and review evidence. Pending/failed/ambiguous gates block advancement. Parallel research requires explicitly reviewed branches, not implied freedom from the diagram. No advancing downstream of E003 until its report, results and decision have been reviewed and the specific next action authorized.

Historical R0 results and current E003 evidence do not retroactively pass future stages. Existing implementation plan and tech-stack documents remain proposals; where scheduling/labels conflict, preserve them and consult the new reconciliation notes rather than rewriting history.

## Preservation and amendments

User instruction: no existing-record changes. Original source-program text, experiment identities and prior evidence stay intact. Corrections or future checkpoints are new, dated files naming the superseded interpretation, reason, author/reviewer, source hashes and affected scope. No silent deletion/replacement of unsuccessful runs. No new successor registration while E003 remains unreviewed.

The archived source content is verified by SHA-256 of its UTF-8/LF representation and a separate attachment hash. This is detectable file consistency, NOT physical write-once storage. Branch protection and immutable artifact hosting are future controls requiring authorization. Do not change the protected source or its hash together and call that preservation.

## Current boundary

Representation/replay foundation exists; downstream adequacy is blocked. See [PROJECT_STATE.md](PROJECT_STATE.md), the live E003 decision and [stage XP001](docs/governance/stages/XP001-domain-model-adequacy.md). The current request authorizes governance documentation only, not implementing required E003 revisions or launching a new experiment.
