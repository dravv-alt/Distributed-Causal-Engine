# Reviewed frontend update: 8 October 2026

The user explicitly requested these decisions and acquisition findings in the frontend. Only presentation source was updated; experiment records, historical snapshots and prior progress reports remain unchanged.

Serve the repository root on localhost:

```powershell
python -m http.server 8080 --bind 127.0.0.1
```

- Main cockpit: http://localhost:8080/frontend/research-cockpit/
- Evidence acquisition: http://localhost:8080/frontend/research-cockpit/#acquisition
- Research notebook: http://localhost:8080/frontend/research-reader-2026-10-08/

Both views now load this directory's new `records.json`. Their older snapshots remain historical. The prior reader README/build command describes that original snapshot, not the updated live presentation. The new exclusive builder is `python -B scripts/build_frontend_reviews_20261008.py`; it refuses replacing an existing output. This snapshot is dated and does not automatically detect subsequent record changes.

## Displayed changes

- E004-R001 execution accepted; scientific REVISE / structural prior only retained. No causal or successful RCA interpretation.
- E002-R002 separate REVISE approved; its tested timing-policy null result does not reject temporal methods generally.
- Removed these two pending-review prompts from the current presentation. Original pending proposals remain accessible as historical records alongside the later amendments.
- Added bounded acquisition stopping questions, observed sample totals, source-level breakdown, limitations, documentation conflicts and original evidence links/hashes.
- Acquisition is complete, while metric qualification, healthy controls and an independent evaluation split remain unestablished. No detector, successor or E005 is authorized.
- Linked the full 8 October progress report with an explicit before-approvals label.

## Verification

`node scripts/audit_frontend_reviews_20261008.cjs` passed in an actual Chromium browser: ten cockpit routes, four notebook experiment views, desktop/mobile widths, approved-review and acquisition text, evidence HTTP links, no runtime exceptions, and simulated request failure with successful Retry recovery. The initial audit attempt's failure injection raced navigation completion; the audit now waits for the acquisition page before injecting the failure. This was a verification timing issue, not an experiment result.

Browser report and screenshots are in `browser-audit-final/`. JavaScript syntax checks passed. All 51 frontend evidence hashes and 188 prior acquisition inputs matched. Both governance checks passed for their respective dated scopes, including preservation of 116 protected records; the historical checker still describes its old E003 checkpoint as pending. No scientific gate was self-approved.

No experiment, dataset scan, commit or push was performed.
