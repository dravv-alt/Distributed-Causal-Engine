# DCE: Distributed Causal Engine (R0 foundation)

Neuro-symbolic incident intelligence for distributed services. This repo is the **canonical implementation**;
the research notebooks are provenance only. Scope follows the PRD: R0 (executable research foundation) is built here,
R1 (deployable pilot) and R2 (production qualification) are not.

```
telemetry ─► synchronized windows ─► neural perception ─┐
                (raw + normalized + mask)   (shared temporal encoder,  ├─► fusion & abstention ─► ranked candidates,
topology (A depends on B) ─► symbolic facts & rules ────┘ per-service scores)        root sets, evidence, uncertainty
```

## Quickstart
```bash
pip install -e ".[dev]"      # numpy, networkx; scikit-learn only for training
pytest -q                    # 28 tests
scripts/reproduce_r0_baseline.sh runs   # simulate -> train -> evaluate (~2 min on 1 CPU)
```
CLI: `dce simulate | train | eval | version`.

## Contracts implemented (PRD section 6)
* **Edge semantics:** `(A,B)` = A depends on B. Symptoms at A are explained by walking toward dependencies; potential impact of B = reverse dependencies. Cycles handled (simple-path search with hop cutoff).
* **Windows:** `(N, time, services, features)`, one real channel per service (no `np.tile`), raw + normalized + observed-mask. Train-only robust normalizer travels in the model bundle.
* **Labels:** detection and forecast are separate functions; forecast labels are strictly after the window.
* **Splits:** chronological train/val/test with embargo = context + horizon. Thresholds are chosen on validation only.
* **Symbolic rules:** observed onsets with uncertainty (missing data widens it), cause-before-effect within per-hop bounds, healthy-intermediate contradiction (an explanation holds if *any* path is uncontradicted), facts carry rule version and input ids.
* **Fusion:** candidates = union(neural, SLO). Neural-only evidence yields `anomaly_only` and never a causal claim. Neural unavailable -> `symbolic_only`, `degraded=true`. Output is `ranking_score` + `confidence_status="uncalibrated"`, with per-branch contributions.
* **Bundles:** `manifest.json` + `weights.npz` (no pickle), checksum verified on load; schema/units/service-order/capacity mismatch rejects inference.
* **Evaluation:** one-to-one incident matching; a detection must be raised inside the event span; alerts raised with no active fault are false positives; repeats counted separately; event-level coverage reported because overlapping faults merge into one incident.

## PRD traceability (honest status)
| Req | Status |
|---|---|
| FEA-01 synchronized windows | Done (tests: distinct channels, no cross-segment windows, train-only stats) |
| FEA-02 preprocessing contract | Partial: schema/units/stats/capacity checked; no degrade-explicitly mode yet |
| NEU-01 neural inference | Partial: real model invocation + compatibility gate; **no deadlines yet** |
| SYM-01 rules | Done for positive/negative/cyclic/concurrent/missing fixtures |
| FUS-01 both branches matter | Done (controlled-change tests + ablations) |
| FUS-02 unknown/multiple origins | Partial: root sets + anomaly_only; no explicit "unknown" beyond abstention |
| OPS-01 deterministic replay | Partial: simulator/eval deterministic; decision-ID replay not built |
| MOD-01 promote/rollback | Partial: checksum + compatibility; no gate/activation |
| TOP-01 versioned topology | Partial: immutable + hashed; no API/provenance store |
| ING, INC, API, UX, NOT, REC, FB, SEC | Not started (R1) |

## R0 synthetic baseline (seeded; NOT evidence of real-world accuracy)
Full tables: `docs/baseline-report-r0.json`. Top-1 = top-ranked candidate is the true root, over all events.

| dataset | events | symbolic_only | neural_only | hybrid | hybrid - best ablation (paired, CI95) |
|---|---|---|---|---|---|
| sparse faults (held-out seed) | 41 | 0.951 | 0.951 | 0.951 | 0.000 [0.000, 0.000] |
| dense/overlapping (held-out seed) | 63 | 0.794 | 0.794 | 0.825 | +0.032 [0.000, 0.079] |
| load x1.5 (drift) | 47 | 0.872 | 0.915 | 0.894 | -0.021 [-0.064, 0.000] |
| 3% telemetry gaps | 44 | 0.818 | 0.818 | 0.818 | 0.000 [0.000, 0.000] |

Reading it honestly:
* **The hybrid does not meet the PRD gate** (>= +5pp Top-1 over the strongest ablation). Per the PRD risk table, keep the stronger baseline and revise fusion/model before any research claim.
* The topology matters: removing it drops root-in-set from ~0.9-0.98 to ~0.55-0.62 and forces abstention.
* The neural branch detects faster (median 1-3 s vs 3-4 s) but **under drift (load x1.5, gaps) it raises false incidents** (incident precision 0.42 / 0.69 vs 1.0 for symbolic-only). The trigger depends on the neural branch (shuffling its scores collapses precision).
* Event recall is 1.0 for every method: the simulated faults are strong. This regime is easy and the simulator's propagation matches the rules' assumptions, which flatters symbolic_only.
* Fault-free: 0 false alerts in 66.7 service-hours (0.35 day). That is too little to support the <=1/day target (rule of three: 95% upper bound ~8.6/day).
* `hybrid_no_timing` matched or beat `hybrid` on two datasets. Unexplained; a hypothesis (not tested) is that mixing neural-derived and SLO-derived onsets makes timing comparisons inconsistent.

## Known limitations / next work
1. Neural drift robustness (training augmentation, feature selection, drift monitor) and alert-budget-matched comparison.
2. Fix onset provenance mixing (neural vs SLO onsets) and test the timing rule on real propagation.
3. Realistic testbed faults; held-out *topology* evaluation (needs per-environment baseline refit).
4. R1: ingestion API, PostgreSQL queue/incident store with transactional outbox, OTel mapping, operator console, webhooks, Docker Compose.
