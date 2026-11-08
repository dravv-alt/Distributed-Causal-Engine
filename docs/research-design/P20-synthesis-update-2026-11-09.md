# P20 campaign synthesis update — 2026-11-09

This dated supplement records current evidence and status conflicts without editing the execution plan, permanent index, prior experiment records, or earlier synthesis notes.

## Evidence and stage status

| Stage | Current evidence | Status and limits |
|---|---|---|
| XP001 | E003 bounded census/replay review accepted 162 V004 profiles matched to manifest paths and V006 reported two 335-case replay passes. | Overall E003 remains **REVISE**. Raw archive hashes/row counts were not recomputed in this checkout; 7,956 metric entries remain semantically unknown; 50 cases lack observed root resources, 160 lack root traces, and two query rows remain unassociated. |
| XP002 | E005-R001 tested delivery, malformed rejection, retry, storage-failure behavior and receiver restart, but source-to-sink metric timestamp fidelity was unknown. E005-R002 then ran through the OpenResearch local backend on frozen commit `1f4591d6081a54588a1dde01152ce0a829848b57`. Its saved-artifact audit passed 13 checks; four metric source tuples matched durable sink tuples exactly. | Evidence is bounded to synthetic loopback fixtures. The successful run does not establish production telemetry quality or RCA effectiveness. An additive human review proposal recommends PROCEED for this limited contract; the E005 decision record remains unchanged and review is pending. The first OpenResearch attempt's port-conflict failure is retained. |
| XP003 | E006-R002 scanned 19 locally present inference files and 833,551 rows from nine frozen RCAEval cases; its independent hash/schema/row/null-count audit passed. | Descriptive sample only, not the full 735-case index. Units, temporality, aggregation, reset semantics, timestamp alignment, and RCA quality remain unestablished. E006's disposition says XP003 is not passed; human review remains pending. |
| XP004–XP038 | The live execution plan currently marks these stages planned/not authorized. Additional experiment amendments and result artifacts exist in the workspace. | Do not count artifacts as stage completion without verifying their registration, protocol, provenance, independent analysis, and review status. This supplement does not allocate IDs or authorize a run. |
| P16 | A participant submission contains eight answer strings and confidence values; a separate scoring note counts 2 correct, 3 partial, and 3 not completed/not answered. | Session timing, evidence paths, participant ID, and independent session observation are absent. The same submission's notes say no responses were collected, and the earlier nonrun disposition says there was no response; preserve this conflict. P16 is incomplete and has no validated usability conclusion. |
| P17 | Existing disposition says there is no common held-out set and no integrated matched-baseline evaluation. | The central claim that the integrated DCE system improves RCA remains untested. |
| P18–P19 | Existing synthesis records a scoped candidate for P18 that is not integrated and a partial 600-case synthetic P19 ablation. | Neither is a complete robustness campaign or global application ablation. |
| P20 | Prior synthesis draft and updates remain open. | Final report and campaign closeout remain incomplete. |

## Status-record mismatch

`docs/governance/execution-plan.json` reports XP001 as partial/review-pending and XP002–XP038 as planned/not authorized. Separate additive amendments register E005 for XP002 and E006 for XP003, and run records exist for both. The permanent `EXPERIMENT_INDEX.md` still says E004 is next available. These differences must be reviewed and reconciled through an additive record before further stage progression; this supplement does not silently choose a replacement source of truth.

The read-only governance checker also continues to report protected-content mismatches for `.gitignore` and `README.md`. No reconciliation was made here.

## Campaign conclusion at this date

The campaign has reproducible evidence for bounded representation/replay, synthetic telemetry attachment, and a nine-case RCAEval feature inventory. It has **not** established that DCE reliably diagnoses distributed-system outages or that neuro-symbolic fusion beats a strong independent baseline on held-out cases. P16–P20 and the remaining XP stages are not complete.

## Next review actions

1. Record the owner's decision on the additive E005-R002 review proposal; retain the existing E005 decision unchanged until that decision is authorized as a new record.
2. Review E006-R002's bounded XP003 finding and disposition.
3. Reconcile the execution-plan/permanent-index status against the E005/E006 amendments through a separate additive governance record.
4. Continue to the next registered stage only after its protocol, dependency, provenance, and review status are reconciled. Keep all runs local and preserve failed attempts.
