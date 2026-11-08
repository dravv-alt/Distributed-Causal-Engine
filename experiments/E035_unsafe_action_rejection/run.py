import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "E035-R001"


def validate(proposal):
    plan, constraints = proposal["plan"], proposal["constraints"]
    violations = []
    if plan["projected_availability"] < constraints["minimum_availability"]:
        violations.append("availability")
    if plan["projected_replicas"] < constraints["minimum_replicas"]:
        violations.append("replicas")
    if plan["risk"] > constraints["maximum_risk"]:
        violations.append("risk")
    return {"accepted": not violations, "reasons": violations}


def main():
    proposals = json.loads((ROOT / "fixtures" / "proposals.json").read_text())
    rows = []
    for proposal in proposals:
        result = validate(proposal)
        rows.append({"case_id": proposal["case_id"], "accepted": result["accepted"],
                     "reasons": result["reasons"]})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "predictions.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(json.dumps({"predictions": len(rows), "labels_loaded": False}, indent=2))


if __name__ == "__main__":
    main()
