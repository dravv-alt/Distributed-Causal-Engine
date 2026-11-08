from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E016_membership_adaptation"
RUN = BASE / "results" / "E016-R001"
sys.path.insert(0, str(ROOT / "src"))
from dce_foundation.representation_v2.service_membership import CANONICAL_EIGHT, FixedEightModel, SharedTopologyModel, service_features


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank(ids, scores):
    return [ids[i] for i in np.argsort(-scores, kind="stable").tolist()]


def predict(case, fixed, dynamic):
    ids = [node["service_id"] for node in case["nodes"]]
    fixed_result = {"status": "REJECTED_MEMBERSHIP_MISMATCH", "ranking": [], "scores": {}}
    if tuple(ids) == CANONICAL_EIGHT:
        x = torch.tensor([[node["signals"] for node in case["nodes"]]], dtype=torch.float32)
        with torch.no_grad():
            scores = fixed(x)[0].numpy()
        fixed_result = {"status": "ACCEPTED", "ranking": rank(ids, scores), "scores": {sid: float(scores[i]) for i, sid in enumerate(ids)}}
    valid_ids, features = service_features(case)
    with torch.no_grad():
        scores = dynamic(torch.from_numpy(features[None, ...]))[0].numpy()
    return {"scenario_id": case["scenario_id"], "n_services": len(ids), "fixed_eight": fixed_result, "shared_topology": {"status": "ACCEPTED", "ranking": rank(valid_ids, scores), "scores": {sid: float(scores[i]) for i, sid in enumerate(valid_ids)}}}


def main():
    torch.set_num_threads(1)
    model_dir = RUN / "models"
    fixed, dynamic = FixedEightModel(), SharedTopologyModel()
    fixed.load_state_dict(torch.load(model_dir / "fixed-eight.pt", map_location="cpu", weights_only=True))
    dynamic.load_state_dict(torch.load(model_dir / "shared-topology.pt", map_location="cpu", weights_only=True))
    fixed.eval(); dynamic.eval()
    input_paths = [BASE / "fixtures" / name for name in ("test-inputs.json", "permutation-inputs.json")]
    cases = []
    for path in input_paths:
        cases.extend(json.loads(path.read_text(encoding="utf-8"))["cases"])
    predictions = [predict(case, fixed, dynamic) for case in cases]
    malformed = []
    base = json.loads((BASE / "fixtures" / "test-inputs.json").read_text(encoding="utf-8"))["cases"][0]
    duplicate = json.loads(json.dumps(base)); duplicate["scenario_id"] = "MALFORMED-DUPLICATE"; duplicate["nodes"][1]["service_id"] = duplicate["nodes"][0]["service_id"]
    dangling = json.loads(json.dumps(base)); dangling["scenario_id"] = "MALFORMED-DANGLING"; dangling["edges"].append([dangling["nodes"][0]["service_id"], "outside"])
    for case in (duplicate, dangling):
        try: service_features(case); result = {"scenario_id": case["scenario_id"], "rejected": False}
        except ValueError: result = {"scenario_id": case["scenario_id"], "rejected": True}
        malformed.append(result)
    out = RUN / "predictions.json"
    out.write_text(json.dumps({"predictions": predictions, "malformed_challenges": malformed}, indent=2) + "\n", encoding="utf-8")
    inputs_hashes = {p.name: sha(p) for p in input_paths}
    model_hashes = {p.name: sha(p) for p in model_dir.glob("*.pt")}
    seal = {"prediction_sha256": sha(out), "input_sha256": inputs_hashes, "model_sha256": model_hashes, "labels_loaded": False, "device": "cpu", "network_used": False, "python": sys.version, "platform": platform.platform(), "torch": torch.__version__, "numpy": np.__version__}
    (RUN / "prediction-seal.json").write_text(json.dumps(seal, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"predictions": len(predictions), "malformed_rejected": sum(x["rejected"] for x in malformed), "sealed": True, "labels_loaded": False}, indent=2))


if __name__ == "__main__": main()
