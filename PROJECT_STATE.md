# DCE context-recovery checkpoint — 2026-10-03

This is a new dated checkpoint, not a replacement scientific record. Verify against [EXPERIMENT_INDEX.md](EXPERIMENT_INDEX.md) and actual experiment artifacts before taking action. Later changes require separately dated checkpoints while the no-existing-record-edits instruction is active.

## Start here after context loss

Read [AGENTS.md](AGENTS.md), [constitution](EXPERIMENTAL_PROTOCOL.md), the register, this checkpoint, live E003 records, [roadmap](docs/governance/EXECUTION_ROADMAP.md), the relevant stage card and applicable scientific contracts. [Machine state](docs/governance/project-state.json) supplies explicit identifiers and gates. `python scripts/check_project_governance.py` performs read-only cross-file consistency checks.

## Permanent identities and current state

| ID | Permanent meaning | Verified record status |
|---|---|---|
| E001 | R0 baseline reproduction | Draft; not executed under this ID |
| E002 | Onset/timing analysis | Reserved; depends on E001 review |
| E003 | Domain model adequacy | R001 executed; downstream adequacy blocked; review pending |

Next available ID: E004; **not allocated or authorized**. Do not confuse source-program E001 domain modeling with permanent E001. Its intent maps to planning XP001 and registered E003.

## Implemented versus planned

- Original five notebooks and delivered R0 remain separate historical/prototype work; do not credit them as executing registered E001/E002.
- `src/dce_foundation/` implements canonical values, ZIP adapter, event time, typed operational/evaluation graphs, validation, inspection and replay. `pyproject.toml` names the separate dce-foundation package; no migration of R0.
- `data/dataset/` holds immutable-source archives in place; `data/manifests/openrca.json` identifies the local snapshot. Raw data/processed samples are ignored. Do not rewrite, extract over originals or publish telemetry by default.
- E003's [report](docs/E003-implementation-report.md), [audit](docs/openrca-dataset-analysis.md), [results](experiments/E003_domain_model_adequacy/results/E003-R001/adequacy.json) and [decision](experiments/E003_domain_model_adequacy/decision.md) are the evidence, not the roadmap.
- Future stages (symbolic/neural/fusion/causal/counterfactual/planning/remediation/production/UI) are **planned only**. Capability claims need their own controls, ablations and gates.

## E003 findings to retain

39 tests passed, including four local-data samples. Eight earliest/latest scopes replayed deterministically with 2,000-row-per-file prefix limits. 100,763 source rows scanned: 98,736 mapped, 2,000 rejected, 27 outside scope; 136,992 observations. These are bounded prefixes, not a full-data or incident-level success claim.

Required revisions awaiting review: seconds/milliseconds variation in Bank trace files; incomplete parent resolution/root conventions; unknown units/temporality/duration/status; entity aliases/kinds/resources; unmapped workbook deployment relations; event-centered/full-day coverage and memory; query/incident association. Successful parsing does not establish semantic adequacy. No silent fix was applied to executed v1 source.

## Next permitted action

**Review E003's report, results and decision with the user.** Present revision options; obtain explicit scope and existing-record/source-change authority before making corrections, registering an experiment or running revised adequacy tests. No downstream work is unlocked by this guideline-adoption request. Governance additions/read-only review remain permitted within their authorized scope.

## Practical recovery notes

Repo root: Distributed-Causal-Engine. PowerShell, `PYTHONPATH=src`. Replay: `python -m dce_foundation.replay.openrca --incident Bank@135 --max-rows-per-file 2000`. This is a reference command, not permission to launch a new scientific run. Existing CLI refuses output overwrites. The v1 adequacy harness hardcodes E003-R001, so do not reuse it as if it allocated safe new run IDs.

The prior sandbox pytest attempt failed on temp-directory permissions; approved execution passed. `.test-tmp-e003` was retained/ignored, not deleted. Existing worktree contains uncommitted/user-owned changes; do not reset, commit or push without authority. No hosted immutability, production deployment or full-volume qualification has been demonstrated.

---

## Context update — 2026-11-05: move away from the inherited OpenRCA dataset

This is an append-only recovery note. It does not alter any historical experiment, result, decision, registry entry, protocol or executed source.

### Latest verified OpenRCA status

The 4 November source-provenance inventory completed the deterministic evidence-qualification step for the 18 metric names selected by the 8 October bounded sample. It found:

- no sampled metric with sufficient semantic qualification;
- no documented healthy-control source; and
- no documented independent evaluation population.

The inventory and stopping report are in `docs/research-design/2026-11-04-source-provenance-inventory/`. Metric meanings, units, kind, temporality, aggregation, reset behavior, exporter/configuration provenance and local-dataset version match remain `UNKNOWN` where unsupported. This is a stop decision for OpenRCA-based detector work, not evidence that distributed-system RCA is impossible.

E004-R001 execution remains accepted with **REVISE / structural prior only**. E002-R002 remains separately approved as **REVISE**. Neither decision authorizes E005, detector development, a successor experiment or production claims.

### User-directed proposed pivot

The user has directed the project away from relying on this inherited dataset and asked about a system that uses logs and a hybrid neuro-symbolic approach to identify distributed-system root causes.

The proposed replacement evidence source is a controlled distributed-system lab that the project owns. It would contain small instrumented services, structured logs, traces, metrics, topology/deployment metadata, controlled fault injection and a recorded ground-truth fault timeline. A future hybrid system would combine learned evidence from logs/metrics/traces with symbolic checks over topology, time ordering and constraints. It must expose evidence, uncertainty and abstention rather than assert an unsupported root cause.

This is a proposed direction only. No Docker or Kubernetes environment, fault injector, telemetry pipeline, neural model, symbolic RCA engine, experiment ID, protocol, dataset, detector or evaluation has been registered, implemented or executed under this pivot.

### Next permitted action

Obtain explicit authority to register a new controlled-testbed experiment and choose its execution environment. Before substantial implementation, freeze the research question, hypothesis, baseline, fault schedule, normal-control definition, train/calibration/test split, leakage controls, acceptance metrics, code/configuration provenance and safety boundary. Do not reuse OpenRCA fault labels or claim that the future system is an established root-cause detector before controlled evaluation.
