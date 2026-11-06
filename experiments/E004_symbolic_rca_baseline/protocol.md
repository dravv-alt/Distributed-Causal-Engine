# E004 protocol v1: restricted structural baseline

Registered before substantial code or E004 predictions. User authorizes E004 execution; the agent defines this bounded, untuned design. Numeric correctness gates below are preregistered engineering criteria, not a separately user-approved accuracy target.

## Inputs and population

Consume exactly 335 Replay-1 artifacts from V006's frozen inventory, including its 164 V004 references and 171 V006 files. Verify byte and canonical hashes, timestamp bounds and edge evidence before ranking. No raw archive scan or context-DB query. Read operational inputs only; fault labels are opened by the evaluator after all predictions are durably written and their hash recorded.

All observed resource tokens form the same candidate universe for all methods. Retain all cases, including missing-root and disconnected cases. Candidate presence is evaluated afterwards and never used for input selection. No identity aliases or service aggregation. Scores are not probabilities. Unknown source units, durations, log messages and metric values are unused.

## Fixed methods and symptom boundary

There is no qualified symptom detector in this scope. Structural candidates are not claims of observed failure. The restricted baseline is intentionally weak.

- **symbolic_topology_v1**: caller-to-callee CALLS edges, supported by same-trace parent evidence within the window. Collapse parallel edges and omit self loops for reachability. Score each observed node by the count of distinct OTHER observed nodes that can reach it along CALLS. This is an explicit shared-dependency heuristic, not a causal edge. Cycles terminate with a visited set. Abstain if no non-self CALLS edges, otherwise rank all observed nodes, including isolated zero-score nodes.
- **activity_reference_v1**: rank by the count of observations per resource across available modalities. Independent function accepts counts only, never graph inputs. Observation volume is not abnormality; differing instrumentation rates are a confounder.
- **graph_disabled_uniform_v1**: all observed nodes receive zero; no graph/count-based score. It is both an independent chance reference and the genuinely graph-disabled topology ablation. Abstain only for an empty candidate universe.

Opaque lexical token order breaks ties for deterministic display only. Primary scoring gives expected credit for uniform ordering WITHIN each equal-score group: if the root has h strictly higher-scored candidates and t tied candidates, Top-k credit is max(0,min(1,(k-h)/t)). Root absent or abstention gives zero. Secondary deterministic metrics use the displayed order. Do not select whichever tie rule performs better.

Store compact operational feature certificates: all nodes, observation counts, collapsed edges and one actual edge/evidence reference per collapsed relation plus multiplicity. Explain scores with reachable-caller lists and the full compact relation certificate; label explanations as structural hypotheses, not mechanisms. No healthy/contradicting-state inference from absence.

## Separation, reproducibility and evaluation

The reasoner receives only opaque nodes, edges or counts. Scenario/time/incident identifiers remain orchestration/evaluator metadata and are not scoring inputs. Exact input metadata and labels are separate records. Fault time supplied the inherited window: explicitly an ORACLE-TIME-CONDITIONED retrospective component benchmark, not online detection. Prediction process does not inspect labels. Evaluator hashes labels before and after and joins by scenario/start/cutoff digest; no row-order join or fuzzy root matching. Score component only, not fault type, onset, duration or official query answer.

Two independent algorithm computations per case must give identical scores, rankings, abstention and explanation; second receives reversed node/edge/count insertion order. Zero randomness or tuning. There is no learned split; all results are descriptive benchmarks, not held-out model-training results. Overlapping windows and shared environments make incident independence questionable.

Report overall 335-case and per-system Top-1/Top-3 (both tie policies), candidate coverage, abstention, edge availability, candidate count, root-absent cases and paired deltas. Report descriptive paired 95% normal-approximation intervals from case-level score differences, explicitly NOT valid significance claims under dependent windows. No favorable subset, post-hoc seeds, thresholds or accuracy gate. RCAEval and official evaluator integration remain outside scope.

## Technical gate and decision

PASS only if all 335 inputs accounted for, zero hash/schema/evidence/leakage violations, 335/335 repeat computations equal, baseline graph independence verified, fixtures and independent certificate/score/evaluation audit pass, predictions persisted before label access, and all predecessor evidence remains unchanged. Independent audit recomputes scores and metrics without importing the ranking implementation. Preserve failures; do not repair scientific controls post-results.

Technical PASS does not prove symbolic superiority or satisfy E003's unknown semantics. Decision proposal remains REVISE/restricted diagnostic readiness unless new evidence justifies a narrower statement; no downstream approval is automatic. Stop for human review after final reports.

Minimum free C: space: 6 GiB. No telemetry copying or large new database. Retain preflight configuration/source/environment, full per-case predictions, evaluator tables, compact certificates, tests, logs, input/source/output hashes, independent audit, summary and plain-language decision. Use a source snapshot rather than claiming committed freeze; commit/push not authorized.
