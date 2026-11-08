import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
groups = ["valid", "availability_violation", "replica_violation", "risk_violation", "combined_violation"]
proposals, labels = [], []
for group in groups:
    for i in range(100):
        availability, replicas, risk = 0.99, 3, 0.10
        if group in ("availability_violation", "combined_violation"):
            availability = 0.80
        if group in ("replica_violation", "combined_violation"):
            replicas = 1
        if group in ("risk_violation", "combined_violation"):
            risk = 0.90
        idx = len(proposals)
        proposals.append({"case_id": f"C{idx+1:04d}", "plan": {
            "action": "synthetic_candidate", "projected_availability": availability,
            "projected_replicas": replicas, "risk": risk}, "constraints": {
            "minimum_availability": 0.95, "minimum_replicas": 2, "maximum_risk": 0.50}})
        labels.append({"case_id": f"C{idx+1:04d}", "class": "valid" if group == "valid" else "unsafe",
                       "violation_group": group})
(ROOT / "fixtures" / "proposals.json").write_text(json.dumps(proposals, indent=2) + "\n")
(ROOT / "evaluator" / "labels.json").write_text(json.dumps(labels, indent=2) + "\n")
