# E003-AM002 telemetry census reconciliation

**Date:** 2026-11-06  
**Type:** Additive evidence reconciliation; no existing record changed  
**Scope:** V004 full-file telemetry CSV census and V006 recovery verification  
**Status:** Mechanical census checks reconcile; human review and two inherited gates remain open. This is not an E003 overall pass.

## Plain-language conclusion

The earlier run V002 stopped after profiling 77 of 162 telemetry CSV files because it hit a storage constraint. The work did not end there: V004 continued and produced one file profile for every telemetry CSV listed in the local OpenRCA archive manifest. V006 then reused those profiles (it did not reread the dataset) and completed two replay passes over all 335 cases. Its recovery audit passed.

That supports a narrow conclusion: **the local telemetry CSV census has complete file-path coverage and internally consistent full-file read records**. It does not establish that every metric's meaning is known, every trace parent relationship is complete, that non-CSV archive contents were exhaustively parsed, that the local snapshot is the exact source release, or that the application is ready to make root-cause claims. Therefore, a reviewer may approve the census-integrity subclaim while the scientific outcome remains **REVISE / restricted downstream readiness**.

## Step-by-step reconciliation

1. **Established the comparison universe.** `data/manifests/openrca.json` lists four local archives and 162 manifest entries whose paths are telemetry CSV files. Those entries include path, declared expanded/compressed sizes, header, and ZIP CRC metadata.
2. **Counted the V004 file profiles.** `experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V004/` contains 162 `file-NNN.json` profiles.
3. **Compared path sets.** All 162 manifest telemetry CSV paths have a profile; there are no missing or extra profile paths. Scenario counts are Bank 40, Market/cloudbed-1 16, Market/cloudbed-2 16, and Telecom 90.
4. **Checked each profile's completion markers.** All 162 profiles say `decision=QUALIFIED`, `crc_eof_verified=true`, and `row_conservation=true`. The profile records full-file row counts and decompressed SHA-256 values. This is evidence reported by the profiling pipeline; this reconciliation did not independently recompute every decompressed file hash from source bytes.
5. **Reconciled totals.** Profiles sum to 523,947,689 rows, 68,652,273,976 expanded bytes, and 8,766,454,887 compressed bytes. The row total is consistent with the published OpenRCA scale quoted in the project evidence, but that similarity alone does not identify the precise upstream release represented by the local archives.
6. **Checked recovery status.** V006 `summary.json` reports `dataset_rescanned=false`, 162 inherited profiles (77 originating in V002), two verified replays of 335/335 cases, `independent_audit_passed=true`, and `repeatable=true`. It says V004 was interrupted during Replay 1 and preserved unchanged. Its gates B and D are explicitly **NOT RETESTED**; they inherit the V004 timestamp census and source/projection provenance. Other listed gates A, C, E, F, G, and H are marked PASS in V006.
7. **Kept the scientific decision separate.** V006 still proposes `REVISE / restricted downstream readiness`, marks review required, and reports 7,956 unknown metric entries and 2 unknown query associations. Its audit is a recovery/artifact/replay audit, not approval of metric semantics or downstream RCA readiness.

## What can receive a pass, and what cannot

| Claim | Evidence-based status |
|---|---|
| Every manifest-listed telemetry CSV has a V004 full-file profile | Reconciled: 162 of 162 |
| V004 profiles report EOF CRC verification and row conservation | Reconciled: 162 of 162; independent recomputation of every content hash was not done here |
| V006 recovery artifacts and two replay passes | V006 reports independent audit passed and 335/335 verified in both replays |
| All local archive entries were fully scanned | Not established; this check covers telemetry CSV profiles, not every non-CSV ZIP entry |
| Local archive is an identified, version-matched upstream release | Unknown; manifest `source_version` is not established |
| All metric meanings, units, temporality, aggregation, reset behavior, and exporter provenance are known | No; the qualification registry retains unknowns |
| All trace links/root conventions are semantically complete | No; structural parsing/replay does not settle missing or unresolved parent semantics |
| E003 downstream feature/RCA readiness | No; REVISE/restricted readiness remains the proposal, with human review pending |

“PASS” should only be used for the bounded mechanical census-integrity claim after a human reviewer accepts this reconciliation. It must not be promoted into an overall E003 pass or a detector-quality claim. No acceptance threshold has been invented or changed here.

## Remediation steps for the remaining unknowns

1. **Metric semantics:** Obtain a versioned metric dictionary and exporter/configuration documentation from the dataset owner. Map each required local metric name to unit, kind, temporality, aggregation, reset behavior, resource identity, and transformations. Record document/version/hash and verify it matches the local archive snapshot. Keep unsupported entries `UNKNOWN`; exclude them from metric-dependent claims until qualified.
2. **Trace connections:** Define expected parent/root semantics from version-matched source documentation, then produce counts for spans, roots, resolved parents, unresolved parents, duplicate IDs, and cross-file references. Separate structurally missing parents from documented root conventions. Have an independent reviewer inspect sampled source-to-canonical chains and boundary cases.
3. **Dataset coverage/version:** Identify and freeze the exact upstream release or obtain a trusted source manifest. Reconcile all ZIP entry paths—not only telemetry CSVs—against archive listings and hashes. If exact release identity cannot be established, keep the version mismatch unknown and narrow all claims to the local snapshot.
4. **Gate closure:** Present this file alongside V004 profiles, the archive manifest, V006 `summary.json`, `independent-audit.json`, and the V006 decision for human review. Specifically resolve whether inherited gates B and D are acceptable for the census-only claim or need a separately authorized non-overwriting check.
5. **Future experiments:** A REVISE result is a result, not proof that no future research is possible. It does not itself authorize a successor run. The current governing records still require E003 review and a separately registered, preregistered, authorized scope before further experimental execution. XP-stage plans are not permanent experiment IDs.

## Artifact locations

- Local source inventory: `data/manifests/openrca.json`
- V004 continuation authorization: `experiments/E003_domain_model_adequacy/qualification/2026-10-04/V004-continuation.md`
- V004 per-file records and source snapshot: `experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V004/`
- V006 recovery protocol/configuration: `experiments/E003_domain_model_adequacy/qualification/2026-10-04/continuation-V006/`
- V006 summary, independent audit, decision, and replay comparison: `experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V006/`
- Metric provenance limitations: `docs/research-design/2026-11-04-source-provenance-inventory/report.md`
- E003 experiment decision and overall boundary: `experiments/E003_domain_model_adequacy/decision.md`

## Review requested

Please review and, if appropriate, approve only the bounded finding that the local manifest's 162 telemetry CSV files are represented by complete V004 profile records and that V006's stated recovery/replay audit passed. Keep metric qualification, trace-semantic completeness, exact source-release identity, and downstream readiness unresolved unless their separate evidence and review gates are satisfied.
