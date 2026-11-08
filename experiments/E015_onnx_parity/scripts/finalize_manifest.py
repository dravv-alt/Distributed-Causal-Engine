from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E015_onnx_parity"
E014 = ROOT / "experiments" / "E014_neural_anomaly_pilot"
OUT = BASE / "results" / "E015-R001"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    parity = json.loads((OUT / "parity.json").read_text(encoding="utf-8"))
    prior_seal_path = E014 / "results" / "E014-R001" / "prediction-seal.json"
    prior_manifest_path = E014 / "results" / "E014-R001" / "artifact-manifest.json"
    source_files = [
        "EXPERIMENT_INDEX_AMENDMENT_2026-11-07_E015.md",
        "experiments/E015_onnx_parity/README.md",
        "experiments/E015_onnx_parity/hypothesis.md",
        "experiments/E015_onnx_parity/protocol.md",
        "experiments/E015_onnx_parity/configuration.json",
        "experiments/E014_neural_anomaly_pilot/scripts/run_predictions.py",
    ]
    source_files += [p.relative_to(ROOT).as_posix() for p in sorted((BASE / "scripts").glob("*.py"))]
    provenance = {
        "run_id": "E015-R001",
        "source_hashes": {name: sha(ROOT / name) for name in source_files},
        "telemetry_hashes": parity["telemetry_hashes"],
        "e014_checkpoint_hashes": parity["e014_checkpoint_hashes"],
        "e014_prediction_seal_sha256": parity["e014_prediction_seal_sha256"],
        "e014_artifact_manifest_sha256": parity["e014_artifact_manifest_sha256"],
        "exported_models": [
            {"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)}
            for p in sorted((OUT / "models").glob("*.onnx"))
        ],
        "environment_versions": parity["versions"],
        "hardware": {"processor": platform.processor(), "logical_cpu_count": os.cpu_count()},
        "network_access": False,
        "labels_opened": False,
    }
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    files = [
        {"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)}
        for p in sorted(OUT.rglob("*"))
        if p.is_file() and p.name != "artifact-manifest.json"
    ]
    (OUT / "artifact-manifest.json").write_text(json.dumps({"run_id": "E015-R001", "files": files}, indent=2) + "\n", encoding="utf-8")
    mismatches = [item["path"] for item in files if sha(OUT / item["path"]) != item["sha256"] or (OUT / item["path"]).stat().st_size != item["bytes"]]
    print(json.dumps({"run_id": "E015-R001", "files": len(files), "mismatches": mismatches}, indent=2))
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
