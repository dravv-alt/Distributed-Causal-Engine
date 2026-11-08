from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E016_membership_adaptation"
sys.path.insert(0, str(ROOT / "src"))

from dce_foundation.representation_v2.service_membership import CANONICAL_EIGHT, FixedEightModel, SharedTopologyModel, service_features


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    torch.manual_seed(16013)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)
    input_path = BASE / "fixtures" / "train-inputs.json"
    labels_path = BASE / "fixtures" / "train-labels.json"
    train = json.loads(input_path.read_text(encoding="utf-8"))["cases"]
    labels = json.loads(labels_path.read_text(encoding="utf-8"))["case_roots"]
    if len(train) != 300 or set(labels) != {case["scenario_id"] for case in train}:
        raise SystemExit("training fixture/label coverage mismatch")

    fixed_x, y = [], []
    dynamic_x = []
    for case in train:
        ids = [node["service_id"] for node in case["nodes"]]
        if tuple(ids) != CANONICAL_EIGHT:
            raise SystemExit("training membership/order is not the frozen canonical eight")
        local = np.asarray([node["signals"] for node in case["nodes"]], dtype=np.float32)
        root_index = ids.index(labels[case["scenario_id"]])
        _, graph_features = service_features(case)
        fixed_x.append(local)
        dynamic_x.append(graph_features)
        y.append(root_index)
    fixed_tensor = torch.from_numpy(np.stack(fixed_x))
    dynamic_tensor = torch.from_numpy(np.stack(dynamic_x))
    target = torch.tensor(y, dtype=torch.long)

    fixed = FixedEightModel()
    opt_fixed = torch.optim.Adam(fixed.parameters(), lr=0.005)
    fixed_losses = []
    for _ in range(60):
        opt_fixed.zero_grad(set_to_none=True)
        loss = F.cross_entropy(fixed(fixed_tensor), target)
        loss.backward()
        opt_fixed.step()
        fixed_losses.append(float(loss.detach()))

    torch.manual_seed(16013)
    dynamic = SharedTopologyModel()
    opt_dynamic = torch.optim.Adam(dynamic.parameters(), lr=0.005)
    dynamic_losses = []
    for _ in range(60):
        opt_dynamic.zero_grad(set_to_none=True)
        loss = F.cross_entropy(dynamic(dynamic_tensor), target)
        loss.backward()
        opt_dynamic.step()
        dynamic_losses.append(float(loss.detach()))

    fixed.eval()
    dynamic.eval()
    model_dir = BASE / "results" / "E016-R001" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    fixed_path = model_dir / "fixed-eight.pt"
    dynamic_path = model_dir / "shared-topology.pt"
    torch.save(fixed.state_dict(), fixed_path)
    torch.save(dynamic.state_dict(), dynamic_path)
    with torch.no_grad():
        fixed_train_accuracy = float((fixed(fixed_tensor).argmax(1) == target).float().mean())
        dynamic_train_accuracy = float((dynamic(dynamic_tensor).argmax(1) == target).float().mean())
    summary = {
        "training_cases": len(train),
        "label_sha256": sha(labels_path),
        "input_sha256": sha(input_path),
        "fixed_final_loss": fixed_losses[-1],
        "dynamic_final_loss": dynamic_losses[-1],
        "fixed_training_top1": fixed_train_accuracy,
        "dynamic_training_top1": dynamic_train_accuracy,
        "model_hashes": {fixed_path.name: sha(fixed_path), dynamic_path.name: sha(dynamic_path)},
        "environment": {"python": sys.version, "platform": platform.platform(), "torch": torch.__version__, "numpy": np.__version__, "device": "cpu"},
        "seed": 16013,
    }
    (model_dir.parent / "training-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"training_cases": 300, "fixed_training_top1": fixed_train_accuracy, "dynamic_training_top1": dynamic_train_accuracy, "model_hashes": summary["model_hashes"]}, indent=2))


if __name__ == "__main__":
    main()
