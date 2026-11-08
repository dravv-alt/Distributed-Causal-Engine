from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import polars as pl
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E015_onnx_parity"
E014 = ROOT / "experiments" / "E014_neural_anomaly_pilot" / "results" / "E014-R001"
OUT = BASE / "results" / "E015-R001"
CASE_IDS = ["blind-case-0002", "blind-case-0003", "blind-case-0004", "blind-case-0005", "blind-case-0006", "blind-case-0007", "blind-case-0008", "blind-case-0009", "RE2-TT-case-0001"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Net(nn.Module):
    def __init__(self, width: int):
        super().__init__()
        hidden = min(64, width)
        self.layers = nn.Sequential(nn.Linear(width, hidden), nn.ReLU(), nn.Linear(hidden, 16), nn.ReLU(), nn.Linear(16, hidden), nn.ReLU(), nn.Linear(hidden, width))

    def forward(self, x):
        return self.layers(x)


def make_input(frame: pl.DataFrame):
    cols = [name for name in frame.columns if name != "time" and frame.schema[name].is_numeric()]
    matrix = frame.select(cols).to_numpy().astype(np.float64, copy=False)
    n_fit = max(2, int(len(matrix) * 0.35))
    train = matrix[:n_fit]
    with np.errstate(all="ignore"):
        median = np.nanmedian(train, axis=0)
        center = np.nanmedian(train, axis=0)
        dispersion = np.nanmedian(np.abs(train - center), axis=0)
    median = np.where(np.isfinite(median), median, 0.0)
    center = np.where(np.isfinite(center), center, 0.0)
    scale = 1.4826 * dispersion
    scale = np.where(np.isfinite(scale) & (scale > 0), scale, 1.0)
    filled = np.where(np.isfinite(matrix), matrix, median)
    normalized = np.clip((filled - center) / scale, -10, 10).astype(np.float32)
    missing = (~np.isfinite(matrix)).astype(np.float32)
    return matrix, normalized, np.concatenate((normalized, missing), axis=1)


def main() -> None:
    report = json.loads((OUT / "parity.json").read_text(encoding="utf-8"))
    seal_path = OUT / "parity-seal.json"
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    parity_path = OUT / "parity.json"
    if sha(parity_path) != seal["parity_sha256"]:
        raise SystemExit("Parity report seal mismatch")
    prior_seal = json.loads((E014 / "prediction-seal.json").read_text(encoding="utf-8"))
    prior_partitions = {item["case_id"]: item for item in prior_seal["case_partitions"]}
    checks = []
    for case_id in CASE_IDS:
        raw, standardized, x_np = make_input(pl.read_parquet(ROOT / "data" / "rcaeval" / "inference" / case_id / "metrics.parquet"))
        checkpoint = E014 / "models" / f"{case_id}.pt"
        onnx_path = OUT / "models" / f"{case_id}.onnx"
        onnx.checker.check_model(onnx.load(str(onnx_path)))
        model = Net(x_np.shape[1])
        model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True))
        model.eval()
        session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
        row_normal = 0
        row_high = int(np.argmax(np.max(np.abs(standardized), axis=1)))
        row_missing = int(np.argmax(np.isnan(raw).sum(axis=1)))
        samples = {
            "normal": x_np[row_normal:row_normal + 1],
            "high_score": x_np[row_high:row_high + 1],
            "missing_mask": x_np[row_missing:row_missing + 1],
            "boundary_batch_16": np.repeat(x_np[row_normal:row_normal + 1], 16, axis=0),
        }
        case_checks = []
        threshold = float(prior_partitions[case_id]["neural_threshold"])
        for kind, sample in samples.items():
            with torch.inference_mode():
                torch_out = model(torch.from_numpy(sample)).numpy()
            ort_out = session.run(["reconstruction"], {"features": sample})[0]
            close = bool(np.allclose(torch_out, ort_out, atol=1e-5, rtol=1e-4))
            torch_score = np.mean((torch_out - sample) ** 2, axis=1)
            ort_score = np.mean((ort_out - sample) ** 2, axis=1)
            decision_match = bool(np.array_equal(torch_score > threshold, ort_score > threshold))
            case_checks.append({"input_kind": kind, "allclose": close, "decision_match": decision_match, "shape": list(sample.shape)})
        matching_record = next(item for item in report["cases"] if item["case_id"] == case_id)
        records_match = case_checks == [{k: item[k] for k in ("input_kind", "allclose", "decision_match", "shape")} for item in matching_record["checks"]]
        checks.append({
            "case_id": case_id,
            "onnx_model_valid": True,
            "cpu_provider": session.get_providers() == ["CPUExecutionProvider"],
            "independent_outputs_match_record": records_match,
            "all_inputs_within_tolerance": all(item["allclose"] for item in case_checks),
            "all_threshold_decisions_match": all(item["decision_match"] for item in case_checks),
        })
    passed = all(
        item["onnx_model_valid"] and item["cpu_provider"] and item["independent_outputs_match_record"] and item["all_inputs_within_tolerance"] and item["all_threshold_decisions_match"]
        for item in checks
    )
    audit = {"run_id": "E015-R001", "status": "PASS" if passed else "FAIL", "case_count": len(checks), "cases": checks, "parity_hash_matches_seal": sha(parity_path) == seal["parity_sha256"]}
    (OUT / "independent-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "case_count": audit["case_count"], "parity_hash_matches_seal": audit["parity_hash_matches_seal"]}, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
