# DCE execution roadmap — structured adoption

Read AGENTS.md → EXPERIMENTAL_PROTOCOL.md → PROJECT_STATE.md → live register/E003 decision before using this roadmap. **Planning is not permission to execute.** No existing records were edited by this adoption.

The full original is [archived](EXECUTION_PROGRAM_ORIGINAL.md). [Reconciliation](RECONCILIATION.md) explains numbering and phase conflicts. [execution-plan.json](execution-plan.json) is the machine-readable dependency/controls/artifact map; each stage has an implementation card. All thresholds and approvals remain pending.

## Current gate

E003-R001 is representation evidence, not downstream adequacy. The only next project action is review of E003's report/results/decision. E001/E002 preserve their permanent meanings; future E-IDs are unallocated. XP001 maps to existing E003; the remaining XP stages do not consume E-numbers.

## Detailed phases and gates

| Phase | Objective | Gate |
|---|---|---|
| P00: Research definition | Connect each component to RQ1–RQ8 and measurable evidence; review G0 before architecture claims. | G00: not_approved |
| P01: Formal world model | Review entities, relations, observations, events, state, evidence, hypotheses, rules, constraints, actions and causal-model contracts. | G01: blocked_review_pending |
| P02: Dataset and experimental environment | Establish versioned real telemetry plus a separately controlled fault-injection environment; distinguish replay from intervention capabilities. | G02: not_approved |
| P03: Experimental distributed system and ingestion | Use minimal instrumented services and trustworthy telemetry attachment before downstream experiments; no production platform expansion. | G03: not_approved |
| P04: Temporal representation | Prove event-time alignment, windows, masks, missing/reset/late and membership semantics before learned models. | G04: not_approved |
| P05: Dynamic distributed-system graph | Validate typed relation direction, cycles, shared dependencies, scoped identities and topology provenance. | G05: not_approved |
| P06: Pure symbolic baseline | Establish topology, time, domain rules, contradictions and multiple-root baselines without neural leakage. | G06: not_approved |
| P07: Neural anomaly evidence | Validate held-out incident detection, preprocessing, ONNX parity and changing memberships after symbolic baselines. | G07: not_approved |
| P08: Evidence fusion | Demonstrate independent component contributions through matched baselines and ablations. | G08: not_approved |
| P09: Causal reasoning | Distinguish observations/hypotheses/causality with documented assumptions and controlled interventions. | G09: not_approved |
| P10: Counterfactual reasoning | Test predicted alternative worlds against controlled intervention outcomes and limits. | G10: not_approved |
| P11: Symbolic planning | Define state/action preconditions/effects/goals and reject constraint-violating plans; compare declared objectives. | G11: not_approved |
| P12: Controlled remediation | Require safety checking and explicit human approval, then verify actual transitions and failed recovery in isolated testbeds. | G12: not_approved |
| P13: Self-healing | Only enable bounded closed-loop autonomy after reviewed diagnosis, planning, safety, execution and verification evidence. | G13: not_approved |
| P14: Neuro-symbolic integration | Validate event extraction, bounded hypothesis generation and symbolic rejection of unsupported neural claims. | G14: not_approved |
| P15: Distributed production architecture | Qualify persistence and scope ownership before API/workers/deployment; Kafka only for measured need. | G15: not_approved |
| P16: Frontend and operator experiments | Build an operator evidence interface after backend qualification; test usability and uncertainty without UI becoming reasoning truth. | G16: not_approved |
| P17: Final evaluation campaign | Compare detection/statistical, topology, temporal, neural, fusion and causal/counterfactual baselines under identical held-out conditions. | G17: not_approved |
| P18: Robustness campaign | Challenge missing/late/duplicate/incorrect data, partial traces, membership/topology changes, novel faults, contradictions and process/DB/network failures. | G18: not_approved |
| P19: Global ablation matrix | Remove neural, topology, temporal, rules, causal, counterfactual, fusion and constraints independently; measure real contributions. | G19: not_approved |
| P20: Final research report | Synthesize reproducible experiment evidence, baselines, ablations, failures, limitations, validity threats and decisions; do not replace negative results with narrative. | G20: not_approved |

The detailed 0–20 phase sequence controls this structured representation; the shorter original overview is preserved, not rewritten. Gates are review labels, not current approvals. Data/testbed and research-definition phases without individual source experiment numbers still require versioned provenance and reviewed outputs. P16–P20 require their own preregistered operator/evaluation/robustness/ablation/report scopes; there are no invented future E-IDs.

## Planning stages (not experiment allocations)

| Planning key | Original label | Stage | Prerequisites | Permanent ID |
|---|---|---|---|---|
| [XP001](stages/XP001-domain-model-adequacy.md) | E001 (historical) | Domain model adequacy | research definition | E003 |
| [XP002](stages/XP002-telemetry-attachment.md) | E002 (historical) | Telemetry attachment | XP001 | unallocated |
| [XP003](stages/XP003-real-feature-coverage.md) | E003 (historical) | Real feature coverage | XP002 | unallocated |
| [XP004](stages/XP004-temporal-correctness.md) | E004 (historical) | Temporal correctness | XP003 | unallocated |
| [XP005](stages/XP005-graph-correctness.md) | E005 (historical) | Graph correctness | XP004 | unallocated |
| [XP006](stages/XP006-topology-only-baseline.md) | E006 (historical) | Topology-only baseline | XP005 | unallocated |
| [XP007](stages/XP007-topology-plus-temporal-reasoning.md) | E007 (historical) | Topology plus temporal reasoning | XP006 | unallocated |
| [XP008](stages/XP008-topology-temporal-domain-rules.md) | E008 (historical) | Topology temporal domain rules | XP007 | unallocated |
| [XP009](stages/XP009-contradiction-handling.md) | E009 (historical) | Contradiction handling | XP008 | unallocated |
| [XP010](stages/XP010-multiple-simultaneous-symbolic-faults.md) | E010 (historical) | Multiple simultaneous symbolic faults | XP008 | unallocated |
| [XP011](stages/XP011-neural-anomaly-baseline.md) | E011 (historical) | Neural anomaly baseline | XP009, XP010 | unallocated |
| [XP012](stages/XP012-pytorch-onnx-parity.md) | E012 (historical) | PyTorch ONNX parity | XP011 | unallocated |
| [XP013](stages/XP013-variable-service-membership.md) | E013 (historical) | Variable service membership | XP012 | unallocated |
| [XP014](stages/XP014-fusion-ablation.md) | E014 (historical) | Fusion ablation | XP013 | unallocated |
| [XP015](stages/XP015-remove-neural-evidence.md) | E015 (historical) | Remove neural evidence | XP014 | unallocated |
| [XP016](stages/XP016-remove-topology.md) | E016 (historical) | Remove topology | XP014 | unallocated |
| [XP017](stages/XP017-remove-temporal-evidence.md) | E017 (historical) | Remove temporal evidence | XP014 | unallocated |
| [XP018](stages/XP018-correlation-versus-causal-hypothesis.md) | E018 (historical) | Correlation versus causal hypothesis | XP015, XP016, XP017 | unallocated |
| [XP019](stages/XP019-controlled-intervention.md) | E019 (historical) | Controlled intervention | XP018 | unallocated |
| [XP020](stages/XP020-causal-model-comparison.md) | E020 (historical) | Causal model comparison | XP019 | unallocated |
| [XP021](stages/XP021-counterfactual-root-cause-test.md) | E021 (historical) | Counterfactual root-cause test | XP020 | unallocated |
| [XP022](stages/XP022-alternative-intervention.md) | E022 (historical) | Alternative intervention | XP021 | unallocated |
| [XP023](stages/XP023-planning-validity.md) | E023 (historical) | Planning validity | XP022 | unallocated |
| [XP024](stages/XP024-constraint-aware-planning.md) | E024 (historical) | Constraint-aware planning | XP023 | unallocated |
| [XP025](stages/XP025-plan-optimality.md) | E025 (historical) | Plan optimality | XP024 | unallocated |
| [XP026](stages/XP026-recommendation-correctness.md) | E026 (historical) | Recommendation correctness | XP025 | unallocated |
| [XP027](stages/XP027-execution-correctness.md) | E027 (historical) | Execution correctness | XP024, XP026 | unallocated |
| [XP028](stages/XP028-failed-remediation.md) | E028 (historical) | Failed remediation | XP027 | unallocated |
| [XP029](stages/XP029-single-fault-self-healing.md) | E029 (historical) | Single-fault self-healing | XP028 | unallocated |
| [XP030](stages/XP030-cascading-self-healing-failure.md) | E030 (historical) | Cascading self-healing failure | XP029 | unallocated |
| [XP031](stages/XP031-multiple-self-healing-faults.md) | E031 (historical) | Multiple self-healing faults | XP029 | unallocated |
| [XP032](stages/XP032-unsafe-action-rejection.md) | E032 (historical) | Unsafe-action rejection | XP029 | unallocated |
| [XP033](stages/XP033-neural-symbolic-event-extraction.md) | E033 (historical) | Neural symbolic event extraction | XP030, XP031, XP032 | unallocated |
| [XP034](stages/XP034-neural-hypothesis-generation.md) | E034 (historical) | Neural hypothesis generation | XP033 | unallocated |
| [XP035](stages/XP035-neural-hallucination-rejection.md) | E035 (historical) | Neural hallucination rejection | XP034 | unallocated |
| [XP036](stages/XP036-crash-safe-persistence.md) | E036 (historical) | Crash-safe persistence | XP035 | unallocated |
| [XP037](stages/XP037-concurrent-workers.md) | E037 (historical) | Concurrent workers | XP036 | unallocated |
| [XP038](stages/XP038-kafka-transition-qualification.md) | E038 (historical) | Kafka transition qualification | XP037 | unallocated |

## Execution contract

Each card includes implementation steps, a baseline, metric families, controls, artifacts, stop conditions and original intent. Adopt numeric thresholds and resolved protocols through reviewed registration before implementing it. Ordinary planning updates cannot rewrite frozen experiments. Under current instruction, corrections/reviews are new dated amendment files, not changes to existing records.

The dependency graph is conservative and may branch only after reviewed authority. Parallel branch comparisons do not bypass prerequisite gates. Kafka is conditional; a reviewed decision retaining PostgreSQL can close its qualification without migration. Final evaluation reports uncertainty and negative results rather than implying every proposed component must survive.

## Campaign outputs beyond the 38 proposals

P16: test operator timeline/topology/candidate/evidence/contradiction/uncertainty/action/reasoning-trace interfaces; UI never generates reasoning truth.

P17: compare statistical detection, topology-only, topology+time, neural-only, neural+symbolic and full causal/counterfactual baselines. Report detection (precision/recall/F1/delay/false positives), localization (Top-1/Top-k/root set), causal/counterfactual consistency, explanation/provenance, planning/safety, recovery/MTTD/MTTR and systems workload/resource metrics.

P18: controlled missing/late/out-of-order/duplicate/incorrect telemetry, partial traces, topology/membership changes, novel/multiple faults, model errors, symbolic contradictions and process/DB/network crashes. Do not confuse source disorder with measured arrival lateness.

P19: independently remove neural, graph, time, domain rules, causal, counterfactual, fusion and constraints under matched incidents/tuning. Runtime evidence must show each disabled component is truly absent.

P20: synthesize problem/RQs/world model/ontology/telemetry/symbolic/neural/fusion/causal/counterfactual/planning/self-healing/methodology/datasets/fault injection/baselines/results/ablations/robustness/failures/systems/limitations/validity threats/future work/conclusion from preserved artifacts. Unqualified components remain limitations, not achievements.

