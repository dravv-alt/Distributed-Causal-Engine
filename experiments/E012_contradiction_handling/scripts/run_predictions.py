from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from dce_foundation.representation_v2.contradiction import infer_case


FIXTURE = ROOT / "experiments" / "E012_contradiction_handling" / "fixtures" / "inference.json"
OUT = ROOT / "experiments" / "E012_contradiction_handling" / "results" / "E012-R001"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if set(raw) != {"fixture_version", "cases", "evidence_provenance"}:
        raise ValueError("unexpected inference fixture fields")
    predictions = [{"case_id": case["case_id"], "methods": infer_case(case)} for case in raw["cases"]]
    OUT.mkdir(parents=True, exist_ok=True)
    pred_path = OUT / "predictions.json"
    pred_path.write_text(json.dumps(predictions, indent=2) + "\n", encoding="utf-8")
    seal = {
        "run_id": "E012-R001",
        "case_count": len(predictions),
        "predictions_sha256": digest(pred_path),
        "inference_fixture_sha256": digest(FIXTURE),
        "evaluator_labels_opened": False,
        "network_access": False,
    }
    (OUT / "prediction-seal.json").write_text(json.dumps(seal, indent=2) + "\n", encoding="utf-8")
    (OUT / "source-provenance.json").write_text(json.dumps({
        "run_id": "E012-R001",
        "implementation_sha256": digest(ROOT / "src/dce_foundation/representation_v2/contradiction.py"),
        "runner_sha256": digest(Path(__file__)),
        "protocol_sha256": digest(ROOT / "experiments/E012_contradiction_handling/protocol.md"),
        "configuration_sha256": digest(ROOT / "experiments/E012_contradiction_handling/configuration.json"),
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(seal, indent=2))


if __name__ == "__main__":
    main()
