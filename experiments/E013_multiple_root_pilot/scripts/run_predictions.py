from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from dce_foundation.representation_v2.multi_root import rank_roots

BASE = ROOT / "experiments" / "E013_multiple_root_pilot"
FIXTURE = BASE / "fixtures" / "inference.json"
OUT = BASE / "results" / "E013-R001"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if set(fixture) != {"fixture_version", "cases", "evidence_provenance"}:
        raise ValueError("unexpected fixture fields")
    rows = []
    for case in fixture["cases"]:
        if set(case) != {"case_id", "candidates", "support"}:
            raise ValueError("unexpected inference case fields")
        rows.append({"case_id": case["case_id"], "methods": rank_roots(case["candidates"], case["support"])})
    OUT.mkdir(parents=True, exist_ok=True)
    pred_path = OUT / "predictions.json"
    pred_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    seal = {
        "run_id": "E013-R001",
        "case_count": len(rows),
        "predictions_sha256": sha(pred_path),
        "inference_fixture_sha256": sha(FIXTURE),
        "evaluator_labels_opened": False,
        "network_access": False,
        "source_sha256": sha(ROOT / "src/dce_foundation/representation_v2/multi_root.py"),
    }
    (OUT / "prediction-seal.json").write_text(json.dumps(seal, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(seal, indent=2))


if __name__ == "__main__":
    main()
