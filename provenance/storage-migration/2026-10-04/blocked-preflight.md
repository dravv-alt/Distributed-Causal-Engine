# Storage migration preflight — BLOCKED, no copy or deletion

Client date: 2026-10-04. This is a new infrastructure record, not an E003 scientific amendment or outcome change.

## Confirmed source inventory

- V002 root: `experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V002/`.
- Completed `file-*.json` profiles: **77**, matching the expected partial state.
- Expected total: **162**. Remaining **85** not completed.
- V002 directory: **1,637,810,554 bytes**.
- Selected rescue interpretation/provenance inventory: **122 files**, **1,638,261,032 bytes**, including all V002 files, logs, qualification documents, failure decision, inherited V001 profiles/preflight/source snapshot and dataset provenance manifest.
- Source hashes recorded for each inventoried file, including the compact context database. The database may contain partially processed rows from the interrupted file; it does not turn that file into a completed profile.
- No completed-run artifact manifest exists; the safety-stop/failure record is retained. No complete replay or overall PASS is represented.

`source-inventory.json` is a source-only inventory. It is NOT a rescue-copy verification manifest. Destination hashes remain null.

## Separate dataset boundary (metadata only)

Source: `C:\Users\bhavv\OneDrive\Desktop\Dravvya(4th Sem)\Projects\Distributed-Causal-Engine\data\dataset`.

Five files, two subordinate directories, **8,766,598,385 bytes**:

| Relative path | Bytes |
| --- | ---: |
| Bank.zip | 2,829,139,841 |
| Market.zip | 2,865,427,796 |
| Telecom.zip | 3,071,992,930 |
| OpenRCA-20261002T162203Z-1-004.zip | 13,469 |
| OpenRCA-20261002T162203Z-1-004/OpenRCA/AppTelecomDeploymentList.xlsx | 24,349 |

The three main archives supply telemetry/labels/queries; the deployment workbook is separately required. The auxiliary archive and original directory layout must also be preserved. No dataset migration, dataset content hashing, extraction or deletion has started. Dataset verification requires a separate manifest after rescue verification; this inventory does not certify dataset backup.

## Blocking checks

- C: free bytes measured: **1,652,727,808**, about **1.54 GiB**.
- The rescue alone is about **1.53 GiB**. Attempting a streamed copy using C:-backed cache could nearly exhaust the drive.
- Google Drive for Desktop processes are installed/running, version path `131.0.2.0`.
- An initial directory lookup observed `G:\My Drive`, but subsequent standard and explicitly approved execution checks could not access it; the latest filesystem drive enumeration exposed only C:. This is an unresolved mount/session-access problem, not evidence that cloud files are missing.
- Actual STREAM versus MIRROR configuration: **UNKNOWN**. Cloud quota, offline-pinning status and completed server upload: **UNKNOWN**.

Google documents that unsynced streamed changes use local cache: https://support.google.com/drive/answer/16631477?hl=en . A visible destination or successful local copy alone does not establish cloud durability.

## Required before continuation

Restore an accessible Google Drive mount and verify Preferences → My Drive syncing options → Stream files. Do not switch modes while there are unsynced changes. Establish cloud quota, online-only destination policy and adequate cache headroom on the cache's physical disk. Free unrelated space with separately scoped authority or provide another suitable physical cache/storage location; do not delete OpenRCA or experiment evidence as a workaround.

Only then create a COPY at `G:\My Drive\DCE-RESCUE\E003-AM002-V002`, independently compare files/sizes/hashes and confirm cloud-backed readability/upload before declaring rescue verified. Dataset copying to `G:\My Drive\DCE\datasets\OpenRCA` stays blocked until that gate passes. No local source deletion is safe at this checkpoint.

## Preservation

No scientific execution resumed. No existing experiment/source/configuration record edited. No original dataset or result moved/deleted. No archive or second full local copy created. No Google Drive destination write performed. Rescue verification, dataset verification, DCE streamed-read test and deletion gate are all **NOT PERFORMED**.
