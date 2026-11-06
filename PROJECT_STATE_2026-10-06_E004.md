# DCE recovery checkpoint: E004-R001 completed, review pending

Date: 2026-10-06 (Asia/Calcutta). This is a new checkpoint authorized by the user's E004 execution request. No previous checkpoint, register, result or executed source was edited.

## Recover current authority

Read the original constitution/register for permanent preservation rules, then:

1. `docs/governance/amendments/2026-10-06-E003-V006-acceptance-and-E004-scope.md`: user's acceptance of E003 infrastructure only; scientific limitations remain.
2. `EXPERIMENT_INDEX_AMENDMENT_2026-10-06_E004.md` and `docs/governance/registrations/E004.json`: additive E004 registration authorized by "Go ahead with the E004".
3. `experiments/E004_symbolic_rca_baseline/` hypothesis, protocol, configuration, run and decision registration records.
4. `experiments/E004_symbolic_rca_baseline/results/E004-R001/` preflight, predictions, metrics, independent audit, preservation, summary, manifest and decision.

The old checker validates the October 3 adoption checkpoint and still reports its historical pending gate. `python -s scripts/check_e004_governance.py` validates the additive current registration without rewriting that checkpoint. Neither checker approves E004's scientific outcome.

## Verified final state

- E004-R001 completed and the execution process exited 0.
- All 335 input windows processed; two equal rank computations per window.
- 27 fixture tests passed; independent forward-closure rank and evaluator audit passed all 335 cases.
- Predictions sealed before the execution evaluator parsed labels.
- Post-finalization read-only check verified all 353 manifest entries and frozen source hashes; 354 files total including the manifest itself; 335 compact certificates; no hash errors.
- 1,119 inherited artifacts checked before/after; V002/V004/V005/V006 preserved. All 116 governance-protected records unchanged.
- No raw dataset scan, dataset migration, model training, commit, push or successor run.
- Output size at verification: 50,207,744 bytes. C: free space then: 28.38 GiB (dated measurement, not a permanent free-space guarantee).

Tie-aware exact-component localization, retaining all 335 cases:

| Method | Top-1 | Top-3 |
|---|---:|---:|
| Structural shared-dependency rule | 3.08% | 8.93% |
| Observation-count reference | 4.78% | 14.93% |
| Uniform graph-disabled reference | 1.80% | 5.41% |

284/335 labelled components are in the operational candidate set; 51 missing-root cases remain included. These are supplied-fault-time, structural-prior results, not an online detector or symptom-supported RCA. Metric semantics remain UNKNOWN. Paired intervals are descriptive only because windows/environments may be dependent. No superiority claim is established.

Final record SHA-256:

- summary: `4859f523607d9e0ae71c77dc2998210bd8add2604d411941a02b8fd97c0a09ee`
- independent audit: `91ff312cfe5c22b6aa2a5d9ca021ee0e046fec5f84a619f62bbc2c5a6ba37681`
- artifact manifest: `a13b38296715707e51228bd78d5273654b33076150fa856170c05ef4e4c7fdd9`

## Next permitted action

Human review of E004's report and proposed REVISE / restricted diagnostic readiness. The graph-only rule scored lower than the observation-count reference in this run. Do not tune against these outputs, silently redefine E004, qualify invented fault symptoms, allocate E005 or begin neural/causal/remediation work without separate reviewed authority. E003's earlier records and limitations stay intact.
