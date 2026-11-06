# DCE frontend evidence and readability audit

Date: 8 October 2026, Asia/Calcutta. Scope: read-only review of recorded research and existing frontend; additive presentation preview. No scientific execution, human gate approval, existing-record update, commit or push.

## Findings

The current research cockpit is substantially current. Its v2 snapshot (generated 6 October) equals a fresh in-memory build after excluding the generation timestamp. All 20 linked source files match their snapshot SHA-256 values. E002 displays R002; E003 displays V006 with limited infrastructure acceptance; E004 uses primary tie-aware scores. A dated snapshot is not stale merely because it is two days old.

| Priority | Finding | Evidence | Presentation correction |
|---|---|---|---|
| High | E001 omits original test failures while displaying a separate 47-pass workspace check. | `experiments/E001/logs/E001-R001.md`: 25 passed, 1 failed, 2 errored; CLI succeeded. `docs/engineering/otlp-intake-implementation.md`: separate full suite 47 passed. | Show both with their scope; never imply the E001 R0 suite passed. Implemented in the additive reader. |
| High | Main decision queue mentions E004 but omits E002-R002's separate pending review. | `current.js` start/home use the adapter's E004-only `next_action`; E002 R002 decision explicitly pending. | Display both pending proposals. Implemented in reader. |
| High | Historical page still contains obsolete next-action instructions, although its top notice identifies it as historical. | `frontend/experiment-control-room/index.html`: asks for E002 environment remediation and says E003 remains blocked. | Keep as archive; use current frontend as entry point. Existing page left intact. |
| Medium | Historical cockpit README gives the old v1 builder and serves only the frontend folder; current page requires v2 and repository-root serving for evidence links. | `frontend/research-cockpit/README.md` versus `CURRENT_RESULTS.md`. | Make launch instructions discoverable. New preview README provides correct links; historical README preserved. |
| Medium | Hypotheses, controls, frozen configuration and why each test was needed are absent from the normal detail flow. | `current.js` experiment renderer; adapter only links a selection of result documents. | Six-part experiment narrative with expandable original design records. Implemented in reader. |
| Medium | Run history is a short list of strings, with no direct entry-by-entry artifact navigation or dates. | `history(e)` and adapter `history` arrays. | Original ledgers accessible in reader; richer dated run cards remain a follow-up proposal, not a fabricated history. |
| Medium | Review provenance is uneven. E003 has a dedicated dated approval; E001/E002 acceptance is reported in handoff and presentation notes without dedicated approval links. | `CURRENT_RESULTS.md`, adapter literals, historical E001/E002 decisions; E003 dated amendment. | Explicitly identify source and scope of review status. Reader does not invent reviewer identities or approval dates. |
| Medium | Browser rejects historical schema, but does not detect changed source files, newly completed runs or stale v2 values. | `load()` only checks schema and experiment count. | Dated verification notice implemented. Future refresh should compare source hashes and reviewed registration/run inventory, and flag differences without approving them. |
| Medium | Adapter and UI assume exactly four experiments and hardcode denominators/narrative. | `build_research_cockpit_current.py` unpacking/indexes, `current.js` length guard, fixed 335 tables. | This preview is explicitly E001–E004. Future generalized inventory should be registration-driven; never allocate E-numbers from roadmap. |
| Low | Per-system E004 table shows Top-1 only. | `systems(e)` in existing current.js. | Reader includes Top-1 and Top-3 for all three methods. |

## Research interpretation retained

- E001 reproduced five report tables on one host; original test failures remain recorded. Hybrid superiority was not established.
- E002-R002 fixed local environment qualification without changing the null ranking result: mean Top-1 difference 0.000 across 237 events. Its own proposal awaits review.
- E003 V006 has 162 inherited source profiles and two 335-window replays. Infrastructure acceptance does not resolve the 7,956 UNKNOWN metric meanings, inherited untested B/D conditions, root coverage or oracle-time limitations. The launcher warning is retained.
- E004 processed all 335 cases. Primary graph Top-1/Top-3: 3.08%/8.93%; counts: 4.78%/14.93%; uniform: 1.80%/5.41%. All 51 absent-root cases remain in the denominator. Technical PASS and scientific REVISE/pending review are separate.
- Historical October 3 checkpoint/register/stage statuses are explained by later additive approval/registration records. No scientific conflict was silently rewritten and no roadmap stage was passed.

## Concrete presentation

Preview: `frontend/research-reader-2026-10-08/`.

Each experiment uses: **why this question → what we did → what happened → what it means → unanswered questions → decision needed**. Execution, scientific disposition and human review have separate visible fields. Design records, unsuccessful history, per-system comparisons and original hashed results remain accessible beneath the explanation. The comparison bars have a common 0–100% scale and exact numbers; no confidence claim is attached.

Build script: `scripts/build_research_reader_20261008.py`. It reads the existing current adapter and original records, verifies 41 unique evidence files, and exclusively creates a new dated JSON file. It refuses to overwrite that preview on rerun. It is not a generalized or automatic refresh service.

## Verification and limits

- Both governance checkers passed: 116 protected files unchanged; additive E004 registration recognized. The legacy checker's pending E003 message is historical.
- Existing DOM-light smoke: 9 routes; primary scores; fetch failure; Retry recovery; historical snapshot rejection passed.
- Real Edge browser via localhost CDP: all 9 existing routes and all 4 reader experiments rendered; expanded evidence links returned HTTP 200; no JavaScript runtime exceptions.
- Reader viewport widths 1440 and 390 had no page-level horizontal overflow. Screenshots reviewed at both sizes. Existing E004 screenshot also inspected.
- Browser evidence: `frontend/research-reader-2026-10-08/browser-audit/report.json` and PNGs. Browser tool: `scripts/audit_research_browser_20261008.cjs`.
- No scientific runs or dataset rescans. Artifact verification checks the cited files, not a new full independent evaluation of every original prediction.
- Keyboard/screen-reader usability and research usability have not been systematically evaluated. Reader failure/Retry code is present, but failure injection was tested on the existing cockpit only.
- Current runtime does not detect source edits after the preview build. E001/E002 review provenance remains weaker than the dedicated E003 approval record.

## Next permitted action

Use the preview to review the explanation and decide whether to authorize integrating its layout into the existing cockpit. Integration needs explicit existing-file edit authority under AGENTS.md's no-existing-record-edits rule. Research progression remains a separate human review of E004 and any specifically authorized successor; this frontend work grants none.
