# E003-AM002 V004 continuation protocol

V004 is a new recorded continuation attempt after V003 blocked during the initial streamed archive-hash read. The E003-AM002 scientific protocol is unchanged: all 162 telemetry sources, all 335 annotation-centred windows, two deterministic projected replays, UNKNOWN semantics, and human review before any downstream work.

V002 remains the authoritative partial run with 77/162 completed profiles. V003 remains blocked with zero inherited or newly completed profiles. V004 verifies the original archive hashes before importing exactly the 77 valid V002 checkpoints. It rescans all other 85 sources from their beginnings. It never imports blocks for V002's interrupted source.

The sole operational change is resilient read-only hashing of Google Drive streamed archives: hashes are calculated in 1 MiB blocks. If a Drive read fails, the reader reopens and resumes at the next unread byte, for at most three retries. A full SHA-256 equality check remains mandatory; a read that cannot complete blocks the run.

The existing 6 GiB minimum free-disk floor and 6 GiB context-store maximum remain mandatory. No source, V002, or V003 artifact may be changed or deleted.
