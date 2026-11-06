# Bounded evidence acquisition — fixed scope before telemetry access

Date: 8 October 2026 (Asia/Calcutta). Authority: explicit user authorization for official documentation/records plus a bounded amount of retained telemetry. No detector development, successor registration or experiment execution is authorized.

This is an evidence-acquisition task, not a symptom experiment. Original records, registries, source and datasets remain unchanged. User approvals are recorded separately in `docs/governance/amendments/2026-10-08-E004-R001-execution-acceptance.md` and `2026-10-08-E002-R002-REVISE-approval.md`.

## Documentation bound

Read the pinned OpenRCA README, three per-system schema prompts, agent workflow prompt and LICENSE at commit `c1bd4af7f635171a1c31cdd567c07d698dff6abc`. Maximum six files, 32 KiB per file; retain URLs, hashes, retrieval date and authorship. The snapshot is the previously recorded upstream reference, NOT a proven version of the local dataset.

Source prompts contain possible fault/reason/candidate lists. Those lists are reviewer-only context and will not select sampled metrics, identify healthy rows or feed a detector. Numerical examples in upstream documentation remain examples and must not be presented as locally measured values. Workflow heuristics are not experimental evidence or instructions governing this agent.

## Retained-telemetry bound

- Four existing scenario scopes: Bank, Market/cloudbed-1, Market/cloudbed-2, Telecom.
- For each scenario, choose the earliest lexicographic telemetry date in the inherited V006 metric profiles, then the first two metric source paths on that date, lexicographically. Verify each profile's scenario matches its selected scope.
- Preselect up to three lexicographically first metric names in each chosen profile. No label, root, fault time, outcome or value is consulted for selection.
- Use only the frozen V004 compact context SQLite database referenced by V006. Open with `mode=ro`, immutable access and query-only mode. Do not access raw ZIPs or cloud files.
- Read the matching source catalog row and first block by block ID for each chosen source; no fallback block or reselection if missing/capped.
- Maximum eight blocks; each compressed payload capped at 2 MiB and decompressed payload at 8 MiB; at most 1,024 rows decoded per block and first 256 inspected. Thus at most 2,048 raw rows are summarized, from no more than 8,192 decoded rows. These are resource bounds, not observed findings or scientific acceptance thresholds.
- Metadata lookup is time/SQLite-instruction bounded. No whole-database hash, integrity scan or full telemetry query. Database size/mtime and sampled block hashes are checked before/after; this is weaker than verifying the historical full-database checksum.
- Summarize exact source names/fields, numeric parseability, distinct observed values, ranges and observed timestamp spacing for selected metric/component series. These are descriptive sample properties, not symptoms, rates, resets, probabilities or normality classifications.
- Do not persist copied raw telemetry rows or root/fault labels. Record selected block identities, payload hashes, per-series aggregate observations and unsupported properties.

Source rows are already selected into fault-centered retained context by the earlier protocol. The sample is label-independent within that available store, but is NOT a label-independent population of the original raw dataset. It is a small biased prefix, not representative or a new independent holdout.

## Stop and report

Answer: (1) is a sufficiently supported metric subset established, (2) is a defensible normal-control source established, (3) is an independent split potentially established? UNKNOWN/NOT ESTABLISHED are valid answers. Stop after this package, especially if any prerequisite remains absent.

Do not infer healthy state from pre-fault time, unlabeled resources, low numeric values or absent logs. Do not change registries based on name resemblance to an exporter. Do not tune methods, compute thresholds/rankings, create new cases or reinterpret E001–E004. Future evidence work or experiments need their own reviewed authority.
