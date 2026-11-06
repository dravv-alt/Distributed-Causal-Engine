# Graph Report - docs  (2026-11-06)

## Corpus Check
- 90 files · ~63,629 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .csv 1)

## Summary
- 75 nodes · 32 edges · 46 communities (1 shown, 45 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Evidence and Data Foundations
- Source Provenance Review
- Governance Record Templates
- Execution Governance
- Document Index
- Frontend Evidence Audit
- E003 Acceptance Scope
- E002 Review Record
- E004 Review Record
- Decision Record Index
- XP001 Domain Model
- XP002 Telemetry Attachment
- XP003 Feature Coverage
- XP004 Temporal Correctness
- XP005 Graph Correctness
- XP006 Topology Baseline
- XP007 Temporal Reasoning
- XP008 Domain Rules
- XP009 Contradiction Handling
- XP010 Multiple Faults
- XP011 Neural Baseline
- XP012 ONNX Parity
- XP013 Membership Changes
- XP014 Fusion Ablation
- XP015 Neural Ablation
- XP016 Topology Ablation
- XP017 Temporal Ablation
- XP018 Causal Claims
- XP019 Controlled Intervention
- XP020 Causal Comparison
- XP021 Counterfactual Test
- XP022 Alternative Intervention
- XP023 Planning Validity
- XP024 Safety Constraints
- XP025 Plan Objectives
- Product Requirements
- cAdvisor Provenance

## God Nodes (most connected - your core abstractions)
1. `Implementation Plan` - 5 edges
2. `XP029 Single Fault Self Healing` - 4 edges
3. `Workspace Map 2026 11 05` - 3 edges
4. `Graph Ontology` - 3 edges
5. `Source Provenance Report` - 3 edges
6. `E003 Implementation Report` - 2 edges
7. `Causal Model` - 2 edges
8. `Domain Model` - 2 edges
9. `Event Time Model` - 2 edges
10. `Execution Checklist` - 2 edges

## Surprising Connections (you probably didn't know these)
- `Otlp Intake Implementation` --implements--> `Implementation Plan`  [INFERRED]
  engineering/otlp-intake-implementation.md → IMPLEMENTATION_PLAN.md
- `Implementation Plan` --conceptually_related_to--> `Causal Model`  [INFERRED]
  IMPLEMENTATION_PLAN.md → causal-model.md
- `Reasoning Semantics` --semantically_similar_to--> `Safety Model`  [INFERRED] [semantically similar]
  reasoning-semantics.md → safety-model.md
- `Symptom Evidence Qualification Assessment` --semantically_similar_to--> `Source Provenance Report`  [INFERRED] [semantically similar]
  research-design/2026-10-08-symptom-evidence/symptom-evidence-qualification-assessment.md → research-design/2026-11-04-source-provenance-inventory/report.md
- `Implementation Plan` --references--> `Evaluation Protocol`  [EXTRACTED]
  IMPLEMENTATION_PLAN.md → evaluation-protocol.md

## Hyperedges (group relationships)
- **Research instrument governed by decision gates** — docs_governance_execution_program_original_execution_program_original, docs_governance_execution_roadmap_execution_roadmap, docs_governance_execution_checklist_execution_checklist [EXTRACTED 0.95]
- **E003 representation evidence and E004 review** — docs_e003_implementation_report_e003_implementation_report, docs_governance_amendments_2026_10_06_e003_v006_acceptance_and_e004_scope_2026_10_06_e003_v006_acceptance_and_e004_scope, docs_governance_amendments_2026_10_08_e004_r001_execution_acceptance_2026_10_08_e004_r001_execution_acceptance [EXTRACTED 1.00]
- **Telemetry ingestion, representation and evaluation** — docs_engineering_otlp_intake_implementation_otlp_intake_implementation, docs_domain_model_domain_model, docs_evaluation_protocol_evaluation_protocol [INFERRED 0.75]

## Communities (46 total, 45 thin omitted)

### Community 0 - "Evidence and Data Foundations"
Cohesion: 0.24
Nodes (8): Domain Model, E003 Implementation Report, Otlp Intake Implementation, Event Time Model, Graph Ontology, Implementation Plan, Openrca Dataset Analysis, Workspace Map 2026 11 05

## Knowledge Gaps
- **39 isolated node(s):** `Frontend Audit 2026 10 08`, `Prd`, `Readme`, `Otlp Intake Implementation`, `Execution Program Original` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 56 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **45 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `XP029 Single Fault Self Healing` connect `Remediation and Safety Studies` to `Future Integration and Reliability`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Implementation Plan` (e.g. with `Otlp Intake Implementation` and `Causal Model`) actually correct?**
  _`Implementation Plan` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Frontend Audit 2026 10 08`, `Prd`, `Readme` to the rest of the system?**
  _39 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `XP030 Cascading Self Healing Failure` connect `Future Integration and Reliability` to `Remediation and Safety Studies`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._