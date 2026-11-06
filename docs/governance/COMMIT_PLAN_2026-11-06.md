# DCE granular commit sequence

Inventory: 2026-11-06 (Asia/Calcutta)  
Base: `main` at `319b50f` (`docs: write comprehensive deep-dive README covering PyTorch model and Symbolic Causal Engine architecture`).  
Scope: commit ordering only. This plan does not stage, commit, push, or change experiment results.

## Workspace snapshot

Git reports **1,298 changed paths**: 53 staged additions, 2 modified tracked files, and 1,243 untracked files. The staged files are all E005-related, but they combine registration, implementation, E005-R001 evidence, and the not-yet-run R002 follow-up. They therefore need to be separated when the commit sequence reaches E005.

Largest untracked groups are E003 (520 paths), E004 (359), E002 (60), governance (54, including this plan), E001 (20), and research design (19). Most E003/E004 counts are provenance and result artifacts; they are not independent source changes. E001/E002 each have a specific record mismatch: their root run ledgers say no runs were recorded, while run-named result directories exist. The plan preserves both sides; it does not promote those directories to registered results.

## Commit rules for this sequence

- Stage explicit path lists. Do not use `git add .` or a broad parent directory.
- One experiment registration/protocol commit precedes its result commits. Each result commit has a defined run/version boundary.
- Keep every failed attempt and its logs with its own run. Do not combine separate run IDs just to reduce commit count.
- Keep E004's 335 per-case certificates together as one logical prediction batch; do not make one commit per certificate.
- Before each commit, inspect `git diff --cached --name-status`. After it, inspect `git show --stat --oneline HEAD` and verify no unrelated paths were included.
- No commit in this plan implies a scientific PASS. No push is included.

## Ordered commit list

### Repository policy and project definition

1. **`chore: define repository file byte handling`** — `.gitattributes` only. It sets Git’s text conversion behavior. Put it first to avoid later line-ending changes in hash-sensitive records.

2. **`chore: define generated and scientific artifact handling`** — modified `.gitignore` only. Review the broad `*.json` rule and all exceptions. Check representative manifests, summaries, frontend data, raw archives, SQLite stores, secrets, and caches with `git check-ignore -v` before committing.

3. **`docs: define DCE purpose and research questions`** — root `PRD.md`, `RESEARCH_QUESTIONS.md`, and `ARCHITECTURE.md`. This establishes purpose and intended system boundaries before detailed contracts or implementation.

4. **`docs: define DCE data and reasoning contracts`** — `docs/PRD.md`, `docs/IMPLEMENTATION_PLAN.md`, `docs/TECH_STACK.md`, `docs/domain-model.md`, `docs/graph-ontology.md`, `docs/event-time-model.md`, `docs/telemetry-contract.md`, `docs/evaluation-protocol.md`, `docs/reasoning-semantics.md`, `docs/causal-model.md`, `docs/planning-model.md`, and `docs/safety-model.md`. Keep proposal text distinct from implemented behavior.

5. **`docs: preserve research constitution and permanent identities`** — `AGENTS.md`, `EXPERIMENTAL_PROTOCOL.md`, `EXPERIMENT_INDEX.md`, `PROJECT_STATE.md`, `PROJECT_STATE_2026-10-06_E004.md`, and `EXPERIMENT_INDEX_AMENDMENT_2026-10-06_E004.md`. These are the root-level rules and historical identity records. Preserve older contents as they are; do not silently rewrite disagreements.

6. **`docs: preserve execution roadmap and dated governance evidence`** — all `docs/governance/**`, including `stages/**`, `amendments/**`, `registrations/**`, templates, machine plan/state, preservation manifest, and this commit plan. Keep the 38 XP cards, original source program, reconciliation notes, and dated reviews together. Any stale/current-state conflict should be identified in a separate dated note rather than edited into an older record.

7. **`docs: update current repository status summary`** — modified root `README.md`, after checking it against the dated E003 and E004 review records. The current README still contains older “E003 review pending / do not run” status text. Update only the current summary and links; preserve historical decision files and retain E004’s `REVISE / structural prior only` outcome. Do not call E005 telemetry ingestion an RCA result.

8. **`docs: add experiment and workspace scaffolding`** — `experiments/_template/**`, plus `notebooks/**`, `models/**`, `evaluation/**`, `replay/**`, and `simulator/**` README/.gitkeep placeholders. These establish repository structure without claiming planned modules are implemented. `deployment/**` is assigned to the OTLP intake commit below because it documents that feature.

### Baseline package and shared data foundations

9. **`baseline: preserve delivered R0 package`** — `dce-r0.zip` and `dce-r0/dce/**`. Keep original package history separate from DCE’s newer `src/dce_foundation` implementation. Check archive/extracted-tree correspondence and exclude caches or temporary pytest directories.

10. **`data: add dataset pointers and schema references`** — `data/README.md`, `data/external/openrca/README.md`, `data/manifests/**`, `data/schemas/**`, `data/raw/.gitkeep`, `data/processed/.gitkeep`, `docs/openrca-dataset-analysis.md`, and `provenance/storage-migration/**`. Commit manifests and schema notes only. Do not add ignored OpenRCA archives or raw/processed telemetry payloads.

11. **`feat: add canonical DCE domain and graph model`** — `pyproject.toml`; `src/dce_foundation/__init__.py`, `domain.py`, `event_time.py`, `graph.py`, `inspection.py`, and `validation.py`; `src/README.md`; and planned-module `.gitkeep` files under `src/causal`, `src/domain`, `src/fusion`, `src/graph`, `src/inference`, `src/persistence`, `src/planning`, `src/reasoning`, `src/telemetry`, and `src/workers`. Keep placeholders labeled as planned.

12. **`feat: add OpenRCA adapter and deterministic replay`** — `src/dce_foundation/telemetry/**`, `src/dce_foundation/replay/**`, `src/dce_foundation/evaluation.py`, and `tests/test_openrca_foundation.py`. This depends on commit 11. Do not mix E003 representation-v2 tests into this commit.

### E001 and E002 — setup first, then each run

13. **`research: register E001 baseline reproduction`** — `experiments/E001/README.md`, `hypothesis.md`, `configuration.yaml`, `run.md`, `decision.md`, `results/README.md`, `figures/README.md`, and `logs/README.md`. This is the experiment’s design and ledger scaffold, not its result.

14. **`research: preserve E001-R001-named artifact directory`** — `experiments/E001/results/E001-R001/**`, `experiments/E001/logs/E001-R001.md`, if present, and no rewritten root ledger. Keep `train`, held-out bundles (`faultfree`, `heldout_load`, `heldout_seed`, `heldout_sparse`, `missing`), `bundle`, manifest, report, summary, and proposal together as artifacts. The current `experiments/E001/run.md` says no runs are recorded; do not call these a registered E001 result until that mismatch is resolved in a dated record.

15. **`research: register E002 onset and timing analysis`** — E002 root files (`README.md`, `hypothesis.md`, `configuration.yaml`, `run.md`, `decision.md`, results/figures/logs READMEs), `environment/**`, `scripts/e002_timing_analysis.py`, `scripts/verify_e002_environment.py`, and `requirements-e002-lock.txt`. This records the environment contract before its run evidence.

16. **`research: preserve E002-R001-named artifact directory`** — `experiments/E002/results/E002-R001/**` and `experiments/E002/logs/E002-R001.md`. Keep all three repeat directories, performance outputs, raw results, frozen configuration, environment amendment, manifest, derived metrics, summary, and proposal together as artifacts. The current `experiments/E002/run.md` says no runs are recorded; do not promote the artifacts to a registered E002 result until that mismatch is resolved in a dated record.

17. **`research: preserve E002-R002-named artifact directory`** — `experiments/E002/results/E002-R002/**`, `experiments/E002/logs/E002-R002.md`, and no rewritten root ledger. Keep resolved configuration, all three repeats, performance outputs, validation, paired comparison, metrics, manifest, summary, and proposal together as artifacts. Do not fold the R001-named artifacts into this commit or claim either run is registered while the root ledger says otherwise.

### E003 — separate each implementation and qualification version

18. **`research: preserve E003-R001 bounded adequacy run`** — E003 root `README.md`, `hypothesis.md`, `protocol.md`, `configuration.yaml`, `run.md`, `decision.md`, `results/README.md`, `figures/README.md`, `logs/README.md`, `results/E003-R001/**`, and `docs/E003-implementation-report.md`. This records the original bounded prefix run and its unresolved adequacy decision before later amendments.

19. **`research: register E003-AM001 representation remediation`** — the design/source files `remediation/2026-10-03/.gitignore`, `canonical-schema.md`, `commands.md`, `configuration.json`, `execution-brief.md`, `final-alignment-checkpoint.md`, `hypothesis.md`, `protocol.md`, `provenance-and-mappings.md`, `rcaeval-readiness.json`, `README.md`, and `logs/README.md`; `src/dce_foundation/representation_v2/**`; and `tests/test_representation_v2.py`. Hold `results/**`, V001/V002/V003 logs, `completion-artifact-manifest.json`, `execution-state.json`, `implementation-checkpoints.md`, `decision.md`, `report.md`, and `run.md` for the corresponding output/finalization commits below. This establishes the amendment’s scoped method and implementation, not RCA performance evidence.

20. **`research: preserve E003-AM001 V001 failure`** — `experiments/E003_domain_model_adequacy/remediation/2026-10-03/results/V001/**`, `logs/V001-failure.md`, and `logs/V001-stdout.log` / `logs/V001-stderr.log`. Preserve the initial SQLite/resource schema failure exactly.

21. **`research: preserve E003-AM001 V002 validation`** — `experiments/E003_domain_model_adequacy/remediation/2026-10-03/results/V002/**`, `logs/V002-review.md`, `logs/V002-stdout.log`, and `logs/V002-stderr.log`. Include the later-discovered workbook resource-kind defect with the result; do not present the mechanical pass by itself.

22. **`research: preserve E003-AM001 V003 correction and final analysis`** — `experiments/E003_domain_model_adequacy/remediation/2026-10-03/results/V003/**`, `logs/V003-stdout.log`, `logs/V003-stderr.log`, `logs/final-tests-stdout.log`, `logs/final-tests-stderr.log`, plus `completion-artifact-manifest.json`, `execution-state.json`, `implementation-checkpoints.md`, `decision.md`, `report.md`, and `run.md`. These files interpret V001–V003 together; include them only after V003 artifacts are present and hash-checked.

23. **`research: register E003-AM002 corpus qualification`** — shared files in `experiments/E003_domain_model_adequacy/qualification/2026-10-04/` (README, protocol, configuration, execution brief/status, run ledger, scope boundaries, alignment/review notes), `src/dce_foundation/qualification/**`, `tests/test_e003_compact.py`, and `tests/test_e003_qualification.py`. Do not include `results/V001`–`results/V006` here. This freezes the qualification method and executable before each run artifact is committed.

24. **`research: preserve E003-AM002 V001 census attempt`** — `qualification/2026-10-04/results/V001/**` and `logs/V001-storage-review.md`. Preserve the interrupted full-census attempt and its actual completed-file boundary.

25. **`research: preserve E003-AM002 V002 continuation`** — `results/V002/**`, V002 stdout/stderr logs, and `storage-amendment.md`. Keep the compact-storage change and inherited-profile checks tied to this continuation.

26. **`research: preserve E003-AM002 V003 continuation`** — `continuation-V003/**`, `V003-continuation.md`, `results/V003/**`, and V003-specific logs. This is its own execution record, not a replacement for V001/V002.

27. **`research: preserve E003-AM002 V004 continuation`** — `continuation-V004/**`, `V004-continuation.md`, `results/V004/**`, and V004-specific logs. Keep all inherited and newly generated artifacts together.

28. **`research: preserve E003-AM002 V005 recovery`** — `continuation-V005/**`, `V005-recovery.md`, `results/V005/**`, and V005-specific logs. Preserve recovery and failure details without folding them into V004 or V006.

29. **`research: preserve E003-AM002 V006 audit and review`** — `continuation-V006/**`, `V006-recovery.md`, `results/V006/**`, `scripts/audit_e003_v006.py`, `scripts/validate_e003_am002.py`, `scripts/validate_e003_am002_recovery.py`, `scripts/finalize_e003_am002.py`, `tests/test_e003_checkpoint_continuation.py`, and `tests/test_e003_independent_review.py`. Include the independent audit, launcher warning, recovered-projection hashes, and user’s limited infrastructure acceptance reference. Do not turn V006 into a claim of RCA accuracy.

### E004 — registration, inference output, then evaluation

30. **`research: register E004 symbolic baseline`** — `experiments/E004_symbolic_rca_baseline/README.md`, `hypothesis.md`, `protocol.md`, `configuration.yaml`, `run.md`, root `decision.md`, `src/dce_foundation/symbolic_e004.py`, `scripts/run_e004.py`, and `tests/test_e004_symbolic.py`. Keep the activity, uniform, and topology methods distinct in the committed protocol.

31. **`research: preserve E004-R001 inputs and execution provenance`** — `results/E004-R001/input-manifest.json`, `preflight.json`, `preservation.json`, `source-snapshot.zip`, `logs/qualification.json`, `logs/tests.json`, and the result `run.md`. This records the frozen input/code/environment basis before the output/evaluation bundle.

32. **`research: preserve E004-R001 predictions and certificates`** — `results/E004-R001/case-results.json`, `certificates/**`, and `prediction-seal.json`. Keep all 335 cases and certificates together because they form one prediction population; do not subdivide individual files across commits.

33. **`research: preserve E004-R001 independent evaluation`** — `artifact-manifest.json`, `independent-audit.json`, `metrics.json`, `repeatability.json`, `results.json`, `summary.json`, `decision.md`, and `logs/**`. Keep the REVISE decision and the full 335-case denominator with the calculated metrics. The result remains a restricted structural baseline.

### Cross-cutting provenance and OTLP implementation

34. **`research: preserve dated OpenRCA acquisition and provenance audits`** — `docs/research-design/2026-10-08-bounded-acquisition/**`, `2026-10-08-symptom-evidence/**`, `2026-11-04-source-provenance-inventory/**`, `2026-11-06-census-reconciliation.md`; `scripts/fetch_openrca_reference_20261008.py`, `scripts/inspect_retained_sample_20261008.py`, `scripts/inspect_symptom_evidence_20261008.py`, `scripts/validate_source_provenance_inventory_20261104.py`; and `tests/test_bounded_evidence_acquisition_20261008.py`. Keep each report with its source hashes and verifier. If any item is required to reproduce E003 or E004, move it to that experiment’s commit rather than duplicate it.

35. **`feat: add reusable local OTLP intake`** — `src/dce_foundation/ingest/**`, `examples/otlp-intake/**`, `deployment/**`, `tests/test_otlp_intake.py`, `requirements-ingest.txt`, `docs/engineering/otlp-intake-implementation.md`, and `docs/otlp-intake-slice.md`. This is shared intake code and engineering validation, separate from E005’s experiment-specific receiver.

### E005 — separate registration, R001 history, R002 protocol, and future output

36. **`research: register E005 telemetry attachment`** — `EXPERIMENT_INDEX_AMENDMENT_2026-11-06_E005.md`, E005 README/hypothesis/protocol/configuration, `collector.yaml`, `receiver.py`, `run_e005_r001.py`, `audit_e005_r001.py`, `run.md` registration portion, and results/log READMEs. Do not include R001 result payloads or R002 follow-up files in this commit.

37. **`research: preserve E005-R001 attempts and audit`** — all `experiments/E005_telemetry_attachment/results/E005-R001/**`, all `results/preflight-E005-R001*.json`, and the E005-R001 run-ledger/review updates. Keep failed attempts 002–006, successful attempt 007, the independent audit, and the unresolved timestamp finding together.

38. **`research: freeze E005-R002 timestamp follow-up`** — `protocol-r002.md`, `configuration-r002.json`, and `run_e005_r002.py`. This is currently staged with the other E005 files but belongs after R001’s evidence. The runner currently finds the Collector through an absolute local workspace path; keep that limitation explicit and include the binary version/hash in runtime provenance. Do not add the 188 MB executable to Git.

39. **`research: record E005-R002 OpenResearch result`** — future `experiments/E005_telemetry_attachment/results/E005-R002/**` artifacts, independent audit, and dated interpretation. This commit does not exist yet. Add it only after the OpenResearch local run finishes and the exact SDK-to-storage timestamp comparison has been independently checked. Keep failures under distinct attempt directories.

### User-facing tools and final maps

40. **`feat: add experiment control room prototype`** — `frontend/experiment-control-room/**`. Keep this prototype separate from the research cockpit.

41. **`feat: add current research cockpit interface`** — `frontend/research-cockpit/**`, including its data, `CURRENT_RESULTS.md`, styles, README, and current entry files. Keep application data with the exact UI build it feeds.

42. **`feat: add cockpit builders and audit evidence`** — `scripts/build_research_cockpit_current.py`, `scripts/build_research_cockpit_data.py`, `scripts/build_frontend_reviews_20261008.py`, `scripts/audit_frontend_reviews_20261008.cjs`, `scripts/audit_research_browser_20261008.cjs`, `tests/cockpit_current_smoke.cjs`, `tests/test_research_cockpit_*.py`, and `docs/FRONTEND_AUDIT_2026-10-08.md`. Keep test/audit claims bounded to what they exercised.

43. **`feat: add dated research reader snapshot`** — `frontend/research-reader-2026-10-08/**`, `scripts/build_research_reader_20261008.py`, and its dated browser-audit files. Keep this separate from the current cockpit.

44. **`feat: add dated research updates snapshot`** — `frontend/research-updates-2026-10-08/**` and its browser-audit files. Preserve the date and do not treat this snapshot as the current entrypoint.

45. **`docs: preserve verified progress report`** — `DCE_PROGRESS_REPORT_2026-10-08.md` and `docs/DCE_PROGRESS_REPORT_VERIFICATION_2026-10-08.json`. Keep the report and the verification describing its claim limits together.

46. **`docs: add generated workspace graph`** — `docs/WORKSPACE_MAP_2026-11-05.md`, `graphify-out/GRAPH_REPORT.md`, `graphify-out/graph.html`, and graphify metadata after refreshing it from the final committed tree. This goes last because it describes the other files and may otherwise be stale.

## Exclusions and files needing separate inspection

- Do not add OpenRCA archives or extracted raw data under `data/dataset/**` or `data/external/openrca/**`. Commit manifests and documentation only.
- Keep raw/processed telemetry, generated model/prediction payloads, secrets, environments, caches, temporary pytest directories, and local databases out of ordinary Git history. The registered synthetic E005 SQLite evidence is an explicit exception only when its path/content is part of the E005-R001 evidence group.
- Keep `tools/e005/otelcol.exe` and its downloaded archive outside Git. They are large local tooling dependencies; record version and hash in the run evidence.
- `scrap/index.html` is not assigned above. Inspect its purpose and provenance before deciding whether it belongs in the repository.
- `graphify-out/**` is generated output, not application source. Refresh and inspect before the optional final map commit.

## Staging order and first action

The current index stages E005 before its dependencies. When applying this plan, first unstage the E005 paths without deleting their working-tree files. Then stage only `.gitattributes` for commit 1. At E005, stage commits 36, 37, and 38 as separate explicit path sets. The E005-R002 output commit follows only after its run and audit.

The workspace map is the final commit because it describes the assembled repository. All commits remain local; pushing is outside this sequence.
