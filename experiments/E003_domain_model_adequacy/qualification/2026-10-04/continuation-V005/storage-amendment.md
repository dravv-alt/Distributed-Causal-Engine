# V005 storage controls

V005 stores only the 171 reconstructed Replay-1 artifacts, the full Replay-2 artifacts, its own manifests, copied small profile records and results. It does not copy V004's 1.8 GiB context database or the 164 valid parent Replay-1 artifacts. It uses the V004 context database read-only.

V005 requires at least the frozen 6 GiB free-space floor at every phase and at least 12 GiB plus that floor before beginning recovery. It does not extract or rescan the original archives, create archive copies, modify Google Drive data, or delete anything.
