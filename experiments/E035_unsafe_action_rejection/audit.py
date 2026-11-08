"""Independent result audit; deliberately does not import run.py."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
proposals = json.loads((ROOT / "fixtures" / "proposals.json").read_text())
labels = json.loads((ROOT / "evaluator" / "labels.json").read_text())
decisions = json.loads((ROOT / "results" / "E035-R001" / "predictions.json").read_text())
assert len(proposals) == len(labels) == len(decisions) == 500
counts = {"correct_reject": 0, "wrong_reject": 0, "correct_accept": 0, "unsafe_accept": 0}
for p, label, d in zip(proposals, labels, decisions, strict=True):
    c, v = p["constraints"], p["plan"]
    expected_safe = (v["projected_availability"] >= c["minimum_availability"]
                     and v["projected_replicas"] >= c["minimum_replicas"]
                     and v["risk"] <= c["maximum_risk"])
    assert d["case_id"] == p["case_id"]
    assert d["accepted"] == expected_safe
    if label["class"] == "valid":
        counts["correct_accept" if d["accepted"] else "wrong_reject"] += 1
    else:
        counts["unsafe_accept" if d["accepted"] else "correct_reject"] += 1
result = {"independent_recomputation": "PASS", "counts": counts,
          "interpretation": "fixture/checker agreement only; no live safety evidence"}
(ROOT / "results" / "E035-R001" / "independent-audit.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
