from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E018_remove_neural"
SOURCE = ROOT / "experiments" / "E017_fusion_ablation" / "scripts" / "generate_fixtures.py"
SPEC = importlib.util.spec_from_file_location("frozen_e017_generator", SOURCE)
GEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GEN)


def main() -> None:
    rng = np.random.default_rng(28015)
    cases, labels = [], {}
    for i in range(600):
        case, label = GEN.make_case(i, rng)
        cases.append(case)
        labels[case["scenario_id"]] = label
    fix = BASE / "fixtures"
    (fix / "evaluator-only").mkdir(parents=True, exist_ok=True)
    (fix / "test-inputs.json").write_text(json.dumps({"version": "synthetic-fusion-v1-seed-28015", "cases": cases}, indent=2) + "\n", encoding="utf-8")
    (fix / "evaluator-only" / "test-labels.json").write_text(json.dumps({"case_labels": labels}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"cases": len(cases), "labels_separated": True, "seed": 28015, "generator": SOURCE.relative_to(ROOT).as_posix()}, indent=2))


if __name__ == "__main__": main()
