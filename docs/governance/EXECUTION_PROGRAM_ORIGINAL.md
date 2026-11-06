Absolutely. **This is the way I think we should run DCE.**

We should stop thinking of it as:

> “Build application → add ML → add symbolic reasoning → add self-healing.”

Instead, treat it as an **experimental research project where the application is the experimental instrument**.

Every major architectural decision must have:

1. a hypothesis,
2. an experiment,
3. a controlled setup,
4. measurable metrics,
5. artifacts,
6. results,
7. failure analysis,
8. a decision,
9. and only then permission to proceed.

The uploaded implementation document already gives us the important engineering sequence—contracts → simulator → temporal model → NetworkX rules → fusion/replay evaluation → PostgreSQL/API/worker → Collector → console → production qualification—and explicitly identifies five initial spikes that must precede extensive infrastructure work. 

I would expand that into the following **DCE Experimental Execution Program**.

---

# DCE — Experimental Execution Program

## 0. The fundamental rule

We maintain **three parallel tracks** throughout the project.

```text
                    DCE RESEARCH PROGRAM
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    SYSTEM BUILDING   RESEARCH EXPERIMENTS   DOCUMENTATION
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                    DECISION GATES
                           │
                           ▼
                    NEXT EXPERIMENT
```

The application is never allowed to evolve independently of the experiments.

---

# 1. Our permanent experiment record

Before writing substantial code, create this repository structure.

```text
DCE/
│
├── README.md
├── PRD.md
├── RESEARCH_QUESTIONS.md
├── ARCHITECTURE.md
├── EXPERIMENT_INDEX.md
│
├── docs/
│   ├── domain-model.md
│   ├── graph-ontology.md
│   ├── reasoning-semantics.md
│   ├── telemetry-contract.md
│   ├── event-time-model.md
│   ├── causal-model.md
│   ├── planning-model.md
│   ├── safety-model.md
│   ├── evaluation-protocol.md
│   └── decisions/
│
├── experiments/
│   ├── E001/
│   │   ├── README.md
│   │   ├── hypothesis.md
│   │   ├── configuration.yaml
│   │   ├── run.md
│   │   ├── results/
│   │   ├── figures/
│   │   ├── logs/
│   │   └── decision.md
│   │
│   ├── E002/
│   └── ...
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── manifests/
│   └── schemas/
│
├── src/
│   ├── domain/
│   ├── telemetry/
│   ├── graph/
│   ├── reasoning/
│   ├── causal/
│   ├── planning/
│   ├── fusion/
│   ├── inference/
│   ├── persistence/
│   └── workers/
│
├── models/
├── replay/
├── simulator/
├── evaluation/
├── notebooks/
└── deployment/
```

Every experiment receives an immutable ID:

```text
E001
E002
E003
...
```

And every experiment records:

```text
Question
Hypothesis
Independent variables
Dependent variables
Controls
Dataset/version
Code version
Configuration
Random seeds
Hardware
Results
Failure cases
Interpretation
Decision
Next experiment
```

That becomes our **scientific lab notebook for the entire project**.

---

# 2. The complete research progression

Here is the entire project at a glance.

```text
PHASE 0
Research definition
       ↓
PHASE 1
Domain model + ontology
       ↓
PHASE 2
Telemetry + dataset + simulator
       ↓
PHASE 3
Real telemetry ingestion
       ↓
PHASE 4
Temporal representation
       ↓
PHASE 5
Distributed-system graph
       ↓
PHASE 6
Pure symbolic RCA
       ↓
PHASE 7
Neural anomaly evidence
       ↓
PHASE 8
Evidence fusion
       ↓
PHASE 9
Causal reasoning
       ↓
PHASE 10
Counterfactual reasoning
       ↓
PHASE 11
Planning
       ↓
PHASE 12
Controlled remediation
       ↓
PHASE 13
Self-healing
       ↓
PHASE 14
Neuro-symbolic integration
       ↓
PHASE 15
Distributed production architecture
       ↓
PHASE 16
Final evaluation + research report
```

But **we do not automatically progress from one phase to the next.**

Each phase has a gate.

---

# PHASE 0 — Research definition

## Objective

Define exactly what we are trying to learn.

Not:

> “Can we build an AIOps platform?”

Instead:

> **Can explicit symbolic representations of distributed-system structure, temporal behavior, evidence, causal mechanisms and constraints improve root-cause reasoning and remediation compared with approaches relying primarily on telemetry-driven statistical/neural evidence?**

---

## Research questions

### RQ1 — Representation

Can distributed-system structure be represented as an explicit graph containing:

```text
services
instances
hosts
resources
requests
traces
events
failures
dependencies
hypotheses
actions
constraints
```

without losing the semantics necessary for reasoning?

### RQ2 — Symbolic reasoning

Does explicit topology + temporal + domain reasoning improve root-cause localization?

### RQ3 — Neural evidence

Does learned anomaly evidence provide information unavailable to purely symbolic reasoning?

### RQ4 — Fusion

Does combining neural and symbolic evidence outperform either branch independently?

### RQ5 — Causality

Can explicit causal models distinguish plausible causal mechanisms from merely correlated telemetry?

### RQ6 — Counterfactuals

Can the system predict consequences of interventions?

### RQ7 — Planning

Can symbolic planning produce constraint-valid remediation plans?

### RQ8 — Self-healing

Can the complete loop diagnose → plan → execute → verify safely under controlled failures?

---

## Deliverable

`RESEARCH_QUESTIONS.md`

### Gate G0

We proceed only if every component of the eventual architecture can be connected to a research question.

---

# PHASE 1 — Formal world model

This is where I want us to spend serious time before implementation.

We define:

```text
Entity
Relation
Observation
Event
State
Evidence
Hypothesis
Rule
Constraint
Action
CausalModel
```

---

## 1.1 Entity model

Example:

```text
Entity
 ├── Service
 ├── Instance
 ├── Host
 ├── Database
 ├── Cache
 ├── Queue
 ├── NetworkLink
 └── Resource
```

---

## 1.2 Observation

```text
Observation =

entity
metric
value
unit
observed_time
arrival_time
source
quality
schema_version
```

Critical distinction:

```text
observed_time != arrival_time
```

because distributed systems reorder messages.

---

## 1.3 Event

```text
Event =

event_type
entity
observed_time
attributes
source
confidence
```

Examples:

```text
CPU_SATURATION
LATENCY_SPIKE
ERROR_RATE_SPIKE
DEPLOYMENT
RESTART
PACKET_LOSS
OOM
CONNECTION_POOL_EXHAUSTION
```

---

## 1.4 Hypothesis

This is extremely important.

```text
Hypothesis
 ├── candidate cause
 ├── predicted effects
 ├── supporting evidence
 ├── contradicting evidence
 ├── temporal consistency
 ├── graph consistency
 ├── causal assumptions
 ├── confidence
 └── provenance
```

---

## 1.5 Action

```text
Action
 ├── preconditions
 ├── effects
 ├── cost
 ├── risk
 ├── reversibility
 └── constraints
```

---

# EXPERIMENT E001 — Domain-model adequacy

### Hypothesis

> Our formal representation can encode the distributed-system states required by the planned reasoning experiments without introducing ad-hoc fields for each experiment.

### Test

Create representative incidents:

* dependency failure
* CPU saturation
* memory pressure
* network degradation
* database overload
* retry storm
* multiple simultaneous faults

Represent all of them using the same schema.

### Measure

```text
schema completeness
number of special-case fields
serialization/reconstruction fidelity
ability to reconstruct state
```

### Gate

If we need experiment-specific hacks:

**STOP → revise ontology.**

---

# PHASE 2 — Dataset + experimental environment

We now establish the reality on which everything operates.

We should use two sources.

## Track A — Real/public telemetry

Use an established AIOps/distributed-system dataset.

The uploaded implementation explicitly requires real feature coverage rather than assuming notebook-only columns, and calls for retraining using the actual available schema. 

## Track B — Controlled fault injection

Build our own reproducible distributed testbed.

Why?

Because public datasets provide:

```text
real observations
```

but controlled experiments provide:

```text
known intervention
known ground truth
known topology
known failure mechanism
```

We need both.

---

# PHASE 3 — Experimental distributed system

Build a small but real system.

For example:

```text
             Client
                │
                ▼
          API Gateway
          /         \
         ▼           ▼
    Service A     Service B
         │           │
         └─────┬─────┘
               ▼
          PostgreSQL
               │
             Redis
```

Each component emits:

```text
metrics
logs
traces
```

through OpenTelemetry.

---

# EXPERIMENT E002 — Telemetry attachment

This is one of the five explicit initial spikes from the implementation plan:

> real OTLP ingestion. 

Test:

```text
Service
 ↓
OTel SDK
 ↓
Collector
 ↓
OTLP/HTTP
 ↓
DCE receiver
 ↓
durable storage
```

Verify:

* malformed payload handling
* retries
* acknowledgment semantics
* metric identity
* units
* timestamps
* resource identity
* trace ingestion

### Gate

No downstream experiment begins until ingestion is trustworthy.

---

# EXPERIMENT E003 — Real feature coverage

Second major spike:

> distinct aligned windows from real metrics. 

Determine:

```text
Which metrics actually exist?
Which are missing?
Which are sampled?
Which have different units?
Which are counters?
Which are histograms?
```

This prevents us from designing models around imaginary features.

---

# PHASE 4 — Temporal representation

Build:

```text
Raw telemetry
      ↓
event-time alignment
      ↓
windows
      ↓
features
      ↓
masks
```

Must support:

* late events
* out-of-order events
* missing metrics
* counter resets
* variable service membership
* multiple sampling rates

The implementation plan explicitly identifies event-time/arrival-time and reset handling as gaps requiring fixtures. 

---

# EXPERIMENT E004 — Temporal correctness

Create synthetic disorder:

```text
event 1 → arrives 100ms late
event 2 → arrives before event 1
event 3 → missing
event 4 → counter reset
```

Compare:

```text
online processing
vs
offline replay
```

### Desired result

Same logical event-time window should produce the same diagnosis regardless of arrival ordering.

### If it fails

We fix the temporal engine **before touching ML**.

---

# PHASE 5 — Dynamic distributed-system graph

Now build the graph.

```text
                Service A
                /       \
           CALLS         CALLS
             ↓             ↓
        Service B       Service C
             │
         READS_FROM
             ↓
          Database
```

But edges have semantics.

Not simply:

```text
A -- B
```

but:

```text
A --CALLS--> B
B --READS_FROM--> DB
B --RUNS_ON--> Host
```

---

# EXPERIMENT E005 — Graph correctness

Explicitly test:

* edge direction
* cycles
* shared dependencies
* multiple roots
* multiple faults
* dependency propagation
* impact propagation

The implementation plan already calls out graph direction/cycles/multiple roots as a required test area. 

---

# PHASE 6 — Pure symbolic baseline

**This is our first major research baseline.**

No neural model.

Input:

```text
topology
+
observations
+
events
+
rules
+
temporal information
```

Output:

```text
candidate root causes
+
evidence
+
reasoning path
```

---

# EXPERIMENT E006 — Topology-only baseline

Use only:

```text
dependency graph
```

Question:

> How much can structural information alone localize?

This establishes a deliberately weak baseline.

---

# EXPERIMENT E007 — Topology + temporal reasoning

Add:

```text
event ordering
onset times
propagation delays
```

Compare against E006.

If temporal information doesn't improve localization, investigate why.

---

# EXPERIMENT E008 — Topology + temporal + domain rules

Add rules such as:

```text
DB overload
+
connection pool saturation
+
service latency
→
DB-related hypothesis
```

Measure improvement.

---

# EXPERIMENT E009 — Contradiction handling

Introduce:

```text
healthy evidence
```

that contradicts a hypothesis.

The system should not simply accumulate supporting evidence.

It must be able to say:

```text
H1:
support = 0.71
contradiction = 0.42
```

and potentially abstain.

---

# EXPERIMENT E010 — Multiple simultaneous faults

Example:

```text
DB overload
+
network packet loss
```

Test whether the reasoner incorrectly collapses everything into one root cause.

This is essential.

---

# PHASE 7 — Neural anomaly branch

Only now do we introduce ML.

The implementation plan already specifies:

```text
PyTorch
↓
training
↓
ONNX
↓
ONNX Runtime
```

with shared preprocessing between training and online paths. 

---

# EXPERIMENT E011 — Neural anomaly baseline

Train a neural model to identify anomalous service windows.

We evaluate:

```text
precision
recall
F1
AUROC where appropriate
detection delay
false positives
```

But incident-level metrics matter more than pretending every timestamp is an independent sample.

---

# EXPERIMENT E012 — PyTorch → ONNX parity

One of the explicit initial spikes:

> CPU model export/parity. 

Verify:

```text
PyTorch output
≈
ONNX Runtime output
```

on:

* normal data
* anomaly data
* boundary shapes
* missing masks

---

# EXPERIMENT E013 — Variable service membership

Test:

```text
8 services
12 services
20 services
```

and changing topology.

This addresses the known weakness of a fixed-node neural architecture. The implementation plan specifically calls for a topology-aware challenger later. 

---

# PHASE 8 — Evidence fusion

Now we combine:

```text
Neural evidence
+
symbolic evidence
+
temporal evidence
+
topological evidence
+
contradictions
+
data quality
```

---

# EXPERIMENT E014 — Fusion ablation

This is explicitly required in the implementation plan. 

Run:

```text
A = neural only

B = symbolic only

C = neural + topology

D = neural + topology + temporal

E = full fusion
```

Measure:

```text
Top-1 RCA
Top-k RCA
path accuracy
false diagnosis
abstention
explanation coverage
```

---

# EXPERIMENT E015 — Remove neural evidence

The implementation plan explicitly requires demonstrating that the neural branch actually changes outcomes. 

Run full system with neural evidence disabled.

---

# EXPERIMENT E016 — Remove topology

Run the same incidents without graph evidence.

Now we can empirically answer:

> Does the symbolic graph actually contribute?

Rather than claiming that it does.

---

# EXPERIMENT E017 — Remove temporal evidence

Same experiment.

This gives us an actual ablation matrix:

| Configuration | Neural | Graph | Temporal | Rules |
| ------------- | -----: | ----: | -------: | ----: |
| A             |      ✓ |       |          |       |
| B             |        |     ✓ |          |     ✓ |
| C             |      ✓ |     ✓ |          |     ✓ |
| D             |      ✓ |     ✓ |        ✓ |     ✓ |

Now we can measure contribution rather than storytelling.

---

# PHASE 9 — Causal reasoning

**This is where we introduce the capability you specifically told me not to remove.**

But we now have the infrastructure required to do it properly.

---

## Causal representation

We distinguish:

```text
OBSERVED
POTENTIAL_CAUSE
CAUSAL_HYPOTHESIS
CAUSAL_RELATION
```

Example:

```text
DB overload
    ↓ ?
connection pool exhaustion
    ↓ ?
request latency
```

The `?` matters.

We haven't proven those edges yet.

---

# EXPERIMENT E018 — Correlation vs causal hypothesis

Create incidents where:

```text
A and B correlate
```

but:

```text
A does not cause B
```

Then incidents where:

```text
A genuinely causes B
```

Question:

> Can our system distinguish the two using topology, temporal structure, domain assumptions and controlled interventions?

---

# EXPERIMENT E019 — Controlled intervention

Inject:

```text
DB CPU saturation
```

Observe:

```text
DB latency
→
connection pool
→
service queue
→
timeouts
```

Then repeat without DB saturation.

This establishes intervention-based evidence.

---

# EXPERIMENT E020 — Causal model comparison

Compare:

```text
observational correlation
vs
structural causal model
```

The uploaded implementation plan correctly treats DoWhy as an **optional offline causal-estimation experiment**, rather than making it a runtime dependency. 

That is exactly how I'd keep it.

---

# PHASE 10 — Counterfactual reasoning

Now we ask:

> What would have happened if X had not occurred?

Example:

```text
Observed:

DB overload
 ↓
B latency
 ↓
A timeout
 ↓
retry storm
```

Counterfactual:

```text
DO(DB overload = false)

What happens?
```

---

# EXPERIMENT E021 — Counterfactual root-cause test

For each incident:

```text
Observed world
vs
counterfactual world
```

Compare predicted downstream states.

Metrics:

```text
counterfactual prediction accuracy
causal path accuracy
intervention consistency
```

---

# EXPERIMENT E022 — Alternative intervention

Test:

```text
scale B
```

versus:

```text
repair DB
```

versus:

```text
reroute traffic
```

Which interventions eliminate the observed failure mechanism according to the model?

This leads directly into planning.

---

# PHASE 11 — Symbolic planning

Now actions become first-class.

```text
State
 ↓
Goal
 ↓
Actions
 ↓
Preconditions
 ↓
Effects
 ↓
Constraints
 ↓
Plan
```

---

# EXPERIMENT E023 — Planning validity

Create incidents and goals:

```text
Current:
DB overloaded

Goal:
latency < threshold
```

Generate candidate plans.

Verify every plan's preconditions/effects.

---

# EXPERIMENT E024 — Constraint-aware planning

Add:

```text
minimum healthy replicas = 2
maximum disruption = 1
availability constraint
budget constraint
```

The planner must reject invalid plans.

---

# EXPERIMENT E025 — Plan optimality

Now compare plans using:

```text
risk
cost
expected recovery
disruption
reversibility
```

We don't call one “best” arbitrarily; the objective function is explicitly defined.

---

# PHASE 12 — Controlled remediation

Now we actually execute actions.

But **only inside the controlled testbed**.

```text
Reasoner
 ↓
Planner
 ↓
Safety checker
 ↓
Human approval
 ↓
Execution
 ↓
Telemetry
 ↓
Verification
```

---

# EXPERIMENT E026 — Recommendation correctness

Before execution:

> Does the recommended action actually address the diagnosed mechanism?

---

# EXPERIMENT E027 — Execution correctness

Execute:

```text
restart
scale
reroute
rollback
```

and verify actual state transitions.

---

# EXPERIMENT E028 — Failed remediation

Intentionally make remediation fail.

For example:

```text
restart B
→
B fails to recover
```

The system must detect:

```text
action != expected effect
```

and return to diagnosis.

---

# PHASE 13 — Self-healing

Now we can finally activate:

```text
closed-loop autonomy
```

Not before.

```text
Fault
 ↓
Detect
 ↓
Diagnose
 ↓
Causal reasoning
 ↓
Counterfactual
 ↓
Plan
 ↓
Safety validation
 ↓
Execute
 ↓
Verify
 ↓
Recover / rollback
```

---

# EXPERIMENT E029 — Single-fault self-healing

One known failure.

Measure:

```text
MTTD
MTTR
diagnosis accuracy
plan validity
recovery success
false remediation
```

---

# EXPERIMENT E030 — Cascading failure

Inject:

```text
DB degradation
 ↓
B degradation
 ↓
A timeout
 ↓
retry storm
```

Evaluate whether the system understands the propagation rather than treating each symptom as independent.

---

# EXPERIMENT E031 — Multiple faults

Inject:

```text
DB overload
+
network degradation
```

This is a major robustness experiment.

---

# EXPERIMENT E032 — Unsafe-action rejection

Give the planner an action that violates:

```text
availability constraint
replica constraint
risk constraint
```

The system must refuse it.

This is extremely important for the eventual self-healing claim.

---

# PHASE 14 — Neuro-symbolic integration

Only after we have:

```text
symbolic baseline
+
neural baseline
+
fusion
+
causal model
+
planning
```

do we call the complete architecture genuinely neuro-symbolic.

The neural component can provide:

```text
anomaly detection
event extraction
latent representations
forecasting
candidate hypothesis generation
```

while symbolic components provide:

```text
structure
constraints
logic
causal mechanisms
planning
explanations
safety
```

---

# EXPERIMENT E033 — Neural → symbolic event extraction

Raw telemetry/log:

```text
"connection pool exhausted..."
```

Neural model:

```text
Event(
    type=CONNECTION_POOL_EXHAUSTION,
    entity=Service_B
)
```

Symbolic system consumes it.

Measure extraction accuracy.

---

# EXPERIMENT E034 — Neural hypothesis generation

Neural model proposes:

```text
Candidate:
DB overload
```

Symbolic system verifies:

```text
topology
temporal ordering
constraints
observations
```

This is a much more interesting neuro-symbolic architecture than simply asking an LLM to produce the RCA.

---

# EXPERIMENT E035 — Neural hallucination rejection

Give the neural component an incorrect hypothesis.

Example:

```text
Neural:
"Network failure"

Actual:
DB overload
```

Symbolic layer should reject it because:

```text
topology inconsistent
temporal evidence inconsistent
network metrics normal
DB evidence strong
```

**This experiment is extremely important.**

It demonstrates why the symbolic layer exists.

---

# PHASE 15 — Full distributed architecture

Only now do we build the larger production-like system.

The uploaded implementation plan's sequence is appropriate here:

```text
Python package
 ↓
PostgreSQL
 ↓
FastAPI
 ↓
analysis worker
 ↓
Collector
 ↓
console
 ↓
OIDC
 ↓
operational deployment
 ↓
Kafka when justified
```

rather than starting with all infrastructure. 

---

# EXPERIMENT E036 — Crash-safe persistence

The implementation plan explicitly calls for:

> crash-safe scope ownership and incident persistence. 

Test crashes:

```text
before DB commit
after DB commit
before notification
after notification
during lease
after lease expiry
```

Verify:

```text
no corrupted state
no duplicate decision
safe replay
correct ownership
```

---

# EXPERIMENT E037 — Concurrent workers

Run:

```text
Worker A
Worker B
Worker C
```

against the same environment.

Test:

```text
leases
fencing
duplicate work
stale commits
recovery
```

---

# EXPERIMENT E038 — Kafka transition

Only if PostgreSQL queue reaches a measured limit.

The plan explicitly says Kafka should be introduced after ownership, replay and delivery contracts are established—not simply because Kafka is a production technology. 

Compare:

```text
PostgreSQL queue
vs
Kafka
```

for:

```text
throughput
latency
replay
failure recovery
operational complexity
```

If PostgreSQL passes the requirements:

**we don't migrate.**

That itself is a valid engineering result.

---

# PHASE 16 — Frontend/operator experiments

Now the UI becomes an experimental interface rather than the main development target.

The implementation plan already specifies React/TypeScript, Cytoscape.js for bounded topology/evidence views, and ECharts for timelines/metric evidence. 

The UI should show:

```text
Incident
│
├── Timeline
├── Topology
├── Candidate causes
├── Evidence
├── Contradictions
├── Causal paths
├── Confidence/uncertainty
├── Recommended actions
└── Reasoning trace
```

Crucially:

> The UI must never become the source of reasoning.

---

# PHASE 17 — Evaluation campaign

Now we conduct the final controlled evaluation.

We need several baselines.

### Baseline A

```text
Telemetry anomaly detection only
```

### Baseline B

```text
Topology-only symbolic
```

### Baseline C

```text
Topology + temporal symbolic
```

### Baseline D

```text
Neural
```

### Baseline E

```text
Neural + symbolic fusion
```

### Baseline F

```text
Full causal/counterfactual system
```

---

# Final evaluation metrics

## Detection

```text
Precision
Recall
F1
False positive rate
Detection delay
```

## Localization

```text
Top-1 accuracy
Top-k accuracy
Root-set accuracy
```

## Causal reasoning

```text
causal path accuracy
intervention consistency
counterfactual accuracy
```

## Explanation

```text
evidence coverage
contradiction handling
provenance completeness
```

## Planning

```text
constraint violations
plan validity
expected recovery
cost
risk
```

## Self-healing

```text
recovery rate
MTTD
MTTR
unsafe-action rate
rollback rate
```

## Systems

```text
ingestion throughput
analysis latency
queue lag
CPU
memory
replay throughput
failure recovery
```

---

# PHASE 18 — Robustness campaign

This is where we deliberately attack our own system.

Test:

```text
missing telemetry
late telemetry
out-of-order telemetry
duplicate telemetry
incorrect metrics
partial traces
topology changes
new services
service removal
multiple failures
unknown failures
novel failure combinations
neural false positives
neural false negatives
symbolic contradictions
worker crashes
database crashes
network interruptions
```

The implementation plan already identifies many of these gaps—missingness, ordering, graph cycles, multiple roots, model mismatch, duplicate decisions, topology changes, and uncalibrated confidence. 

---

# PHASE 19 — Ablation matrix

This becomes one of the most important research documents.

We systematically remove components.

```text
Full system

- neural
- topology
- temporal reasoning
- domain rules
- causal model
- counterfactual model
- evidence fusion
- constraints
```

Then measure what breaks.

The question becomes:

> **Which architectural components actually contribute to performance and reliability?**

rather than:

> “We built a complicated architecture, therefore it works.”

---

# PHASE 20 — Final research report

At the end, the paper/report should essentially write itself from the experiment records.

Structure:

```text
1. Abstract

2. Problem Definition

3. Research Questions

4. Distributed-System Model

5. Knowledge Graph Ontology

6. Telemetry Architecture

7. Symbolic Reasoning Architecture

8. Neural Architecture

9. Evidence Fusion

10. Causal Reasoning

11. Counterfactual Reasoning

12. Planning

13. Self-Healing Architecture

14. Experimental Methodology

15. Datasets

16. Fault Injection Methodology

17. Baselines

18. Results

19. Ablation Studies

20. Robustness Studies

21. Failure Analysis

22. Systems Evaluation

23. Limitations

24. Threats to Validity

25. Future Work

26. Conclusion
```

---

# The decision system

This is the most important part of your request.

We **do not blindly execute E001 → E002 → E003.**

Every experiment produces:

```text
                    EXPERIMENT
                         │
                         ▼
                     RESULTS
                         │
             ┌───────────┴───────────┐
             │                       │
          SUCCESS                  FAILURE
             │                       │
             ▼                       ▼
       Advance phase            Diagnose failure
                                     │
                              ┌──────┴──────┐
                              ▼             ▼
                         Model issue   Engineering issue
                              │             │
                              ▼             ▼
                         revise model   fix implementation
                              │             │
                              └──────┬──────┘
                                     ▼
                                RE-RUN TEST
```

Every `decision.md` contains:

```text
Experiment:
E014

Question:
Does fusion improve RCA?

Result:
...

Statistical result:
...

Observed failure:
...

Interpretation:
...

Decision:
PROCEED / REVISE / ABANDON / BRANCH

Reason:
...

Next experiment:
E015
```

---

# The five possible decisions

We should standardize them.

### `PROCEED`

Evidence supports the approach.

### `REVISE`

Idea appears promising but implementation/model is insufficient.

### `REPEAT`

Experiment was contaminated or insufficiently controlled.

### `BRANCH`

Results reveal two interesting approaches worth comparing.

### `ABANDON`

Evidence shows the approach does not justify its complexity.

This last one is **important**.

A serious research project needs permission to kill its own ideas.

---

# The experiment dependency graph

Our actual project should therefore look like this:

```text
E001 Domain model
       │
       ▼
E002 OTLP ingestion ───────┐
       │                   │
       ▼                   │
E003 Real feature schema   │
       │                   │
       ▼                   │
E004 Temporal engine       │
       │                   │
       ▼                   │
E005 Knowledge graph       │
       │                   │
       ▼                   │
E006 Topology baseline     │
       │                   │
       ▼                   │
E007 Temporal baseline     │
       │                   │
       ▼                   │
E008 Symbolic rules        │
       │                   │
       ├── E009 contradictions
       │
       └── E010 multiple faults
       │
       ▼
E011 Neural baseline
       │
       ▼
E012 ONNX parity
       │
       ▼
E013 Dynamic topology
       │
       ▼
E014 Fusion
       │
       ├── E015 remove neural
       ├── E016 remove graph
       └── E017 remove temporal
       │
       ▼
E018 Causal hypothesis
       │
       ▼
E019 Intervention
       │
       ▼
E020 Causal estimation
       │
       ▼
E021 Counterfactual
       │
       ▼
E022 Intervention comparison
       │
       ▼
E023 Planning
       │
       ▼
E024 Constraints
       │
       ▼
E025 Plan evaluation
       │
       ▼
E026 Recommendation
       │
       ▼
E027 Controlled execution
       │
       ▼
E028 Failed remediation
       │
       ▼
E029 Self-healing
       │
       ├── E030 cascading failures
       ├── E031 multiple faults
       └── E032 unsafe actions
       │
       ▼
E033 Neural event extraction
       │
       ▼
E034 Neural hypothesis generation
       │
       ▼
E035 Neural hallucination rejection
       │
       ▼
E036 Crash safety
       │
       ▼
E037 Worker concurrency
       │
       ▼
E038 Kafka qualification
       │
       ▼
FINAL EVALUATION
```

And this is **not necessarily a straight line**.

For example:

```text
E014 Fusion
     ↓
fusion fails
     ↓
return to
E008 symbolic representation
```

or:

```text
E019 intervention
     ↓
causal hypothesis fails
     ↓
revise causal model
     ↓
E018 again
```

That is exactly what we want.

---

# What we should build first

Despite the enormous final architecture, **our immediate implementation is surprisingly small.**

The first development milestone should contain only:

```text
Python domain package
        +
formal schemas
        +
synthetic/replay environment
        +
telemetry normalization
        +
temporal windows
        +
NetworkX graph
        +
symbolic reasoner
        +
evaluation harness
        +
experiment registry
```

This aligns with the implementation plan's adoption order: contracts, Python package, NumPy windows, simulator, shared temporal model, NetworkX rules, fusion and replay evaluation before PostgreSQL/FastAPI/container infrastructure. 

**We should not build React first.**

**We should not build Kafka first.**

**We should not build self-healing first.**

**We should not train a huge neural network first.**

And importantly:

**we should not even call the system “causal” until E018–E020 have given us evidence that the causal layer is doing something beyond correlation.**

---

# The research artifact chain

At every point, we should be able to retrace the project:

```text
Research Question
      ↓
Hypothesis
      ↓
Experiment Design
      ↓
Dataset Version
      ↓
Code Version
      ↓
Configuration
      ↓
Experiment Run
      ↓
Raw Results
      ↓
Analysis
      ↓
Figures/Tables
      ↓
Failure Analysis
      ↓
Decision
      ↓
Architecture Change
      ↓
Next Experiment
```

This is what will make the project **reproducible**.

Six months later, you should be able to open:

```text
experiments/E014/
```

and understand **exactly why we added or rejected fusion**, what dataset was used, what code ran, what happened, and what experiment followed.

---

# One thing I would add to the existing implementation plan

I would create one new top-level document:

## `EXPERIMENTAL_PROTOCOL.md`

It defines the rules of the laboratory itself:

```text
1. No architectural claim without an experiment.

2. No experiment without a hypothesis.

3. No result without a baseline.

4. No comparison without controlled variables.

5. Every model has a version.

6. Every dataset has a manifest.

7. Every run has a seed/configuration.

8. Every result has raw artifacts.

9. Every failure is documented.

10. Every major architecture change gets a decision record.

11. Ablations are mandatory for claimed component contributions.

12. Causal claims require intervention/assumption documentation.

13. Self-healing claims require controlled execution evidence.

14. Performance claims require defined workload and hardware.

15. Reproducibility is an explicit evaluation criterion.
```

That document becomes our **constitution for the project**.

---

## And this is how I want us to work together on it

Rather than me giving you a giant implementation once and you disappearing into 20,000 lines of code, we do:

**Experiment → implementation → run → inspect result → document → decision → next experiment.**

So if E007 produces an unexpected result, **we stop there**. We don't blindly continue to E008 just because the roadmap says so.

If the topology representation is inadequate, we redesign it.

If the neural branch contributes nothing, we investigate whether the model is wrong—or whether neural evidence isn't useful for that task.

If PostgreSQL handles the workload adequately, we don't add Kafka merely for resume value.

If causal reasoning cannot be justified by our available interventions, we document that limitation rather than manufacture a causal claim.

That is what will make this feel like a **real research + systems project rather than a very large portfolio application**.

And it also means that the final result can contain something much more valuable than *“I built an AIOps neuro-symbolic platform.”*

It can say:

> **Here is the hypothesis. Here is the system we built to test it. Here are the controlled experiments. Here are the baselines and ablations. Here is where the approach worked, where it failed, why it failed, and which architectural decisions were justified by evidence.**

That is the standard I would use for DCE.

