# E003-AM002 V005 recovery protocol

V005 is an execution-recovery run, not a new E-number and not a scientific-protocol revision. Its parent is V004, which is preserved unchanged after interruption during Replay 1. V005 must not open raw OpenRCA archives or rescan the 162 telemetry sources.

It reads V004's `context.sqlite` with SQLite read-only mode, validates the 165 preserved Replay-1 files against the exact 335 windows derived from V004 labels and the frozen 300-second pre-fault configuration, reuses only valid parent artifacts by external reference, reconstructs the one corrupt and 170 missing windows in V005, and requires 335/335 coverage before creating Replay 2.

The frozen lineage is: 162 inherited source profiles; 77 inherited V002 profiles; 164 valid V004 Replay-1 artifacts; one corrupt V004 Replay-1 artifact; 170 missing V004 Replay-1 artifacts; 171 V005 reconstructions. Existing V002 and V004 trees are fingerprinted before and after execution. Any mutation, storage-floor breach, artifact mismatch, missing window, duplicate identity or repeatability mismatch blocks V005 and writes a new failure record.

Technical completion is not a scientific E003 PASS. Independent audit and human review remain mandatory.
