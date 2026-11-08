from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E014_neural_anomaly_pilot"
OUT = BASE / "results" / "E014-R001"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    seal = json.loads((OUT / "prediction-seal.json").read_text(encoding="utf-8"))
    evaluator_files = [
        "data/rcaeval/evaluator-only/index-afeacb1/cases.parquet",
        "data/rcaeval/evaluator-only/sample-selection-2026-11-07.json",
        "data/rcaeval/evaluator-only/selection-manifest.json",
    ]
    source_files = [
        "EXPERIMENT_INDEX_AMENDMENT_2026-11-07_E014.md",
        "experiments/E014_neural_anomaly_pilot/README.md",
        "experiments/E014_neural_anomaly_pilot/hypothesis.md",
        "experiments/E014_neural_anomaly_pilot/protocol.md",
        "experiments/E014_neural_anomaly_pilot/configuration.json",
    ]
    source_files += [p.relative_to(ROOT).as_posix() for p in sorted((BASE / "scripts").glob("*.py"))]
    provenance = {
        "run_id": "E014-R001",
        "inference_inputs": seal["inference_input_hashes"],
        "evaluator_files_sha256": {name: sha(ROOT / name) for name in evaluator_files},
        "source_files_sha256": {name: sha(ROOT / name) for name in source_files},
        "prediction_sha256": seal["predictions_sha256"],
        "model_files": [
            {"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)}
            for p in sorted((OUT / "models").glob("*.pt"))
        ],
        "environment": seal["environment"],
        "hardware": {"processor": platform.processor(), "logical_cpu_count": os.cpu_count()},
        "evaluator_index_sha256": json.loads((OUT / "evaluation.json").read_text(encoding="utf-8"))["evaluator_index_sha256"],
    }
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    files = [
        {"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)}
        for p in sorted(OUT.rglob("*"))
        if p.is_file() and p.name != "artifact-manifest.json"
    ]
    (OUT / "artifact-manifest.json").write_text(json.dumps({"run_id": "E014-R001", "files": files}, indent=2) + "\n", encoding="utf-8")
    mismatches = [item["path"] for item in files if sha(OUT / item["path"]) != item["sha256"] or (OUT / item["path"]).stat().st_size != item["bytes"]]
    print(json.dumps({"run_id": "E014-R001", "artifact_count": len(files), "mismatches": mismatches}, indent=2))
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
