# DCE coding-agent entry point

These repository instructions apply to all DCE work. Higher-priority system/developer instructions and explicit user instructions still govern. This file makes the research policy discoverable to coding agents that support AGENTS.md; it does not technically constrain every tool or service.

## Mandatory context recovery before task actions

Read these files fully, in this order:

1. `EXPERIMENTAL_PROTOCOL.md` — laboratory constitution.
2. `PROJECT_STATE.md` and `docs/governance/project-state.json` — dated recovery checkpoint; verify against live records.
3. `EXPERIMENT_INDEX.md` — authoritative permanent experiment identities.
4. The active experiment's hypothesis, protocol (if present), configuration, run ledger, results and decision. Currently `experiments/E003_domain_model_adequacy/`.
5. `docs/governance/EXECUTION_ROADMAP.md`, `docs/governance/execution-plan.json`, and the relevant `docs/governance/stages/` card.
6. Applicable scientific contracts in `docs/`, plus the implementation/source evidence relevant to the task. Do not infer implementation readiness from a roadmap.

Run `python scripts/check_project_governance.py` for read-only consistency checks when practical. It is not a substitute for reading the evidence or reviewing a gate. If files disagree, report the conflict and stop advancement; never silently reconcile scientific records.

## Permanent constraints

- The application is an experimental instrument. System building, controlled research and documentation progress together through reviewed decision gates.
- Current user instruction: **DO NOT CHANGE ANY EXISTING RECORDS.** Add new files only. Do not edit existing experiment/register/protocol/configuration/run/result/decision files, historical docs or executed source to turn a failed result into success. Ask for explicit authority before changing an existing record. Store proposed corrections as separate dated amendments, preserving originals.
- E001 = R0 baseline reproduction; E002 = onset/timing analysis; E003 = domain model adequacy. The register wins over historical labels in the archived guideline.
- Planning IDs `XP001`–`XP038` are not experiment IDs. Never create future E-number folders or allocate IDs merely because the roadmap lists a stage. Registration requires reviewed authority and compliance with the immutable register.
- E003-R001 is executed but downstream adequacy is NOT established. Human review is pending. The next action is review, not automatic model repair, rerun, new experiment, reasoning, ML, infrastructure or remediation.
- Documentation/governance work authorized by the user is allowed without passing E003. Read-only diagnostics may support review. Neither action grants implementation or execution authority for future stages.
- Preserve raw archives, original notebooks and delivered R0. Keep `dce_foundation` distinct from the R0 `dce` package. Protect unrelated dirty changes. Do not commit or push without authorization.
- No labels/fault schedules/scoring points in inference inputs. No fabricated units, aliases, durations, topology, evidence, hypotheses, causal edges or results. UNKNOWN is valid evidence of inadequacy.
- No RCA/neural/causal/planning/self-healing/infrastructure work under the current E003 task. Future stages require their own preregistration, evidence and reviewed authorization.
- No causal claims from correlation; require assumptions and interventions. No self-healing claims without controlled execution/safety/recovery evidence. Kafka is conditional on measured need, not a mandatory milestone.

## Each authorized execution

Name the research question, permanent experiment ID, approved scope and prerequisite gate. Register/freeze protocol with controls/baselines, acceptance metrics, dataset/code/configuration/environment provenance before substantial code. Execute only the approved scope, retain failures and artifact hashes, evaluate independently, then document interpretation and request gate review. Never self-approve a human decision or blindly advance to the next card.

Finish with implemented scope, verified results, unresolved issues, artifact locations and the next permitted action. Update recovery state only through a newly authorized, separate checkpoint/amendment while the no-existing-record-edits instruction remains in force. Do not update private agent memory unless explicitly requested.
