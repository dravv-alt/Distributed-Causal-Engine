# E003-AM002 V006 single recovery pass

User authorized one controlled pass to finish the preserved V004 checkpoint. V002, V004 and V005 remain immutable source evidence. This is execution recovery under E003; no new experiment identity is allocated.

Research question and scientific protocol remain the AM002 qualification question and protocol.md. Canonical projection, timestamp interpretation, 300-second pre-fault windows, filtering, units, topology and serialization remain the frozen V004 configuration/source. Existing dated governance recovery documents are preserved; later explicit authorization permits this bounded execution but does not pass a scientific gate.

Before execution: create profiles/, cases/replay-001/, cases/replay-002/, logs/. Hash all preserved run files before/after. Freeze implementation/environment/configuration/source snapshot. Open V004 context.sqlite in SQLite mode=ro. Validate profiles against catalog/row counts/EOF and 77 inherited V002 hashes. No original dataset access.

Derive 335 distinct windows from preserved labels. Read the 165 existing replay artifacts; validate gzip/JSON/bounds/projected fields/evidence. Reuse 164 by immutable path and hash reference without repeating their Replay-1 projections. Record the corrupt and missing windows and reconstruct only 171. Validate the whole referenced/generated 335-window union. Replay 2 independently regenerates all 335 projections from the same read-only context; compare canonical and graph hashes. Independent artifact reader verifies both runs. No inherited artifact is considered repeatable until Replay 2 hash equality succeeds.

Safety: 6 GiB free floor retained; reserve estimated 12 GiB output before start; additional guards before writes. No context copy, extraction, deletion, migration, or source census. Ordinary initialization issues may be repaired in this same authorized run with recorded provenance. Scientifically unsafe conditions produce failure.json; no automatic V007.

Final evidence: summary.json, artifact-manifest.json, independent-audit.json, results.json, decision.md, inventories, source snapshot, parent integrity and execution logs. Technical replay completion is separated from semantic/evaluator readiness and requires human scientific review. Unknown metric semantics and unresolved associations stay explicit. Untested scientific conditions remain NOT RETESTED.

Command: PYTHONPATH=src; .venv-e002/Scripts/python.exe -m dce_foundation.qualification.recovery_v006 --output experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V006
