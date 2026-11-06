# DCE Research Cockpit

The cockpit is a read-only decision interface for E001-R001, E002-R001, and E003-R001. It is not a DCE runtime, monitoring dashboard, experiment runner, or source of scientific truth.

## Generate and view

From the repository root:

```powershell
python scripts/build_research_cockpit_data.py
python -m http.server 8080 --directory frontend/research-cockpit
```

Open `http://localhost:8080`.

The adapter reads existing artifacts and writes only `frontend/research-cockpit/data/experiments.json`. It fails when a required source is missing. Experiment records are never changed to suit the UI.

Before presenting a new experiment result, regenerate the data after the run has been reviewed. The UI must not be used to promote a pending/revised/blocked result as approved.
