# Experiment Control Room

This is a deliberately simple, static decision dashboard. It does not run DCE, modify experiment evidence, or hide uncertainty. Its content is a human-readable snapshot of E001-R001, E002-R001, and E003-R001.

From the repository root, run:

```powershell
python -m http.server 8080 --directory frontend/experiment-control-room
```

Then open `http://localhost:8080`. The evidence links point back to the local experiment artifacts. Update the displayed statements only alongside a reviewed experiment decision; do not use the dashboard to turn a pending or failed gate green.
