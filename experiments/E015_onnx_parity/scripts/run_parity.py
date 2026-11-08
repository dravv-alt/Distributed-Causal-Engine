from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import statistics
import sys
import time
import traceback

import numpy as np
import onnx
import onnxruntime as ort
import polars as pl
import torch
from torch import nn


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E015_onnx_parity"
E014 = ROOT / "experiments" / "E014_neural_anomaly_pilot"
CASES = ["blind-case-0002", "blind-case-0003", "blind-case-0004", "blind-case-0005", "blind-case-0006", "blind-case-0007", "blind-case-0008", "blind-case-0009", "RE2-TT-case-0001"]
ATOL = 1e-5
RTOL = 1e-4


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


class Autoencoder(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        width = min(64, input_dim)
        self.layers = nn.Sequential(
            nn.Linear(input_dim, width), nn.ReLU(),
            nn.Linear(width, 16), nn.ReLU(),
            nn.Linear(16, width), nn.ReLU(),
            nn.Linear(width, input_dim),
        )

    def forward(self, x):
        return self.layers(x)


def preprocessed_inputs(frame: pl.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    features = [c for c in frame.columns if c != "time" and frame.schema[c].is_numeric()]
    raw = frame.select(features).to_numpy().astype(np.float64, copy=False)
    fit_end = max(2, int(len(raw) * 0.35))
    fit = raw[:fit_end]
    with np.errstate(all="ignore"):
        med = np.nanmedian(fit, axis=0)
        center = np.nanmedian(fit, axis=0)
        mad = np.nanmedian(np.abs(fit - center), axis=0)
    med = np.where(np.isfinite(med), med, 0.0)
    center = np.where(np.isfinite(center), center, 0.0)
    scale = 1.4826 * mad
    scale = np.where(np.isfinite(scale) & (scale > 0), scale, 1.0)
    values = np.where(np.isfinite(raw), raw, med)
    z = np.clip((values - center) / scale, -10.0, 10.0).astype(np.float32)
    mask = (~np.isfinite(raw)).astype(np.float32)
    model_input = np.concatenate([z, mask], axis=1)
    return raw, z, model_input


def median_latency(call, warmup: int = 10, repeats: int = 100) -> float:
    for _ in range(warmup):
        call()
    values = []
    for _ in range(repeats):
        start = time.perf_counter_ns()
        call()
        values.append((time.perf_counter_ns() - start) / 1_000_000)
    return statistics.median(values)


def main() -> None:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    e014_out = E014 / "results" / "E014-R001"
    seal = json.loads((e014_out / "prediction-seal.json").read_text(encoding="utf-8"))
    if sha(e014_out / "predictions.jsonl") != seal["predictions_sha256"]:
        raise SystemExit("E014 prediction seal mismatch")
    partitions = {x["case_id"]: x for x in seal["case_partitions"]}
    e014_manifest = json.loads((e014_out / "artifact-manifest.json").read_text(encoding="utf-8"))
    e014_artifact_errors = [x["path"] for x in e014_manifest["files"] if sha(e014_out / x["path"]) != x["sha256"]]
    if e014_artifact_errors:
        raise SystemExit(f"E014 artifact manifest mismatch: {e014_artifact_errors[:3]}")

    output_dir = BASE / "results" / "E015-R001"
    onnx_dir = output_dir / "models"
    onnx_dir.mkdir(parents=True, exist_ok=True)
    case_results = []
    all_decisions_match = True
    all_values_close = True
    telemetry_hashes = {}

    for case_id in CASES:
        checkpoint = e014_out / "models" / f"{case_id}.pt"
        checkpoint_hash = sha(checkpoint)
        if checkpoint_hash != partitions[case_id]["model_sha256"]:
            raise SystemExit(f"E014 checkpoint hash mismatch: {case_id}")
        telemetry = ROOT / "data" / "rcaeval" / "inference" / case_id / "metrics.parquet"
        telemetry_hashes[telemetry.relative_to(ROOT).as_posix()] = sha(telemetry)
        frame = pl.read_parquet(telemetry)
        raw, standardized, inputs = preprocessed_inputs(frame)
        model = Autoencoder(inputs.shape[1])
        state = torch.load(checkpoint, map_location="cpu", weights_only=True)
        model.load_state_dict(state)
        model.eval()
        onnx_path = onnx_dir / f"{case_id}.onnx"
        sample = torch.from_numpy(inputs[:1])
        export_record = {"case_id": case_id, "checkpoint_sha256": checkpoint_hash, "input_width": inputs.shape[1], "feature_count": raw.shape[1]}
        try:
            torch.onnx.export(
                model, sample, onnx_path,
                input_names=["features"], output_names=["reconstruction"],
                dynamic_axes={"features": {0: "batch"}, "reconstruction": {0: "batch"}},
                opset_version=17, dynamo=False,
            )
            onnx_model = onnx.load(str(onnx_path))
            onnx.checker.check_model(onnx_model)
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 1
            session = ort.InferenceSession(str(onnx_path), sess_options=opts, providers=["CPUExecutionProvider"])
            threshold = float(partitions[case_id]["neural_threshold"])

            # Input selection uses telemetry and the frozen scaler only; no evaluator fields.
            normal_idx = 0
            high_idx = int(np.argmax(np.max(np.abs(standardized), axis=1)))
            missing_idx = int(np.argmax(np.isnan(raw).sum(axis=1)))
            input_cases = {
                "normal": inputs[normal_idx:normal_idx + 1],
                "high_score": inputs[high_idx:high_idx + 1],
                "missing_mask": inputs[missing_idx:missing_idx + 1],
                "boundary_batch_16": np.repeat(inputs[normal_idx:normal_idx + 1], 16, axis=0),
            }
            case_checks = []
            decision_matches = True
            values_close = True
            max_abs_error = 0.0
            max_rel_error = 0.0
            for name, sample_np in input_cases.items():
                sample_t = torch.from_numpy(sample_np)
                with torch.inference_mode():
                    torch_out = model(sample_t).numpy()
                ort_out = session.run(["reconstruction"], {"features": sample_np})[0]
                abs_error = np.abs(torch_out - ort_out)
                rel_error = abs_error / np.maximum(np.abs(torch_out), 1e-12)
                close = bool(np.allclose(torch_out, ort_out, atol=ATOL, rtol=RTOL))
                torch_scores = np.mean((torch_out - sample_np) ** 2, axis=1)
                ort_scores = np.mean((ort_out - sample_np) ** 2, axis=1)
                decisions_equal = bool(np.array_equal(torch_scores > threshold, ort_scores > threshold))
                case_checks.append({
                    "input_kind": name,
                    "shape": list(sample_np.shape),
                    "missing_values_in_source_row": int(np.isnan(raw[normal_idx if name == "normal" or name.startswith("boundary") else high_idx if name == "high_score" else missing_idx]).sum()),
                    "max_absolute_error": float(abs_error.max(initial=0.0)),
                    "max_relative_error": float(rel_error.max(initial=0.0)),
                    "allclose": close,
                    "decision_match": decisions_equal,
                })
                max_abs_error = max(max_abs_error, float(abs_error.max(initial=0.0)))
                max_rel_error = max(max_rel_error, float(rel_error.max(initial=0.0)))
                values_close &= close
                decision_matches &= decisions_equal

            # Latency is measured on matching batch sizes in each local CPU runtime.
            batch1 = input_cases["normal"]
            batch16 = input_cases["boundary_batch_16"]
            with torch.inference_mode():
                torch_ms_1 = median_latency(lambda: model(torch.from_numpy(batch1)).numpy())
                torch_ms_16 = median_latency(lambda: model(torch.from_numpy(batch16)).numpy())
            ort_ms_1 = median_latency(lambda: session.run(["reconstruction"], {"features": batch1}))
            ort_ms_16 = median_latency(lambda: session.run(["reconstruction"], {"features": batch16}))
            export_record.update({
                "status": "PASS" if values_close and decision_matches else "PARITY_MISMATCH",
                "onnx_sha256": sha(onnx_path),
                "checks": case_checks,
                "max_absolute_error": max_abs_error,
                "max_relative_error": max_rel_error,
                "values_within_tolerance": values_close,
                "threshold_decisions_match": decision_matches,
                "latency_median_ms": {"pytorch_batch_1": torch_ms_1, "onnxruntime_batch_1": ort_ms_1, "pytorch_batch_16": torch_ms_16, "onnxruntime_batch_16": ort_ms_16},
                "latency_repeats": 100,
                "latency_warmup": 10,
            })
            all_values_close &= values_close
            all_decisions_match &= decision_matches
        except Exception as exc:
            export_record.update({"status": "EXPORT_OR_RUNTIME_FAILURE", "error": repr(exc), "traceback": traceback.format_exc()})
            all_values_close = False
            all_decisions_match = False
        case_results.append(export_record)

    result = {
        "run_id": "E015-R001",
        "scope": "PyTorch and ONNX runtime parity only; no quality evaluation",
        "case_count": len(case_results),
        "passed_cases": sum(row["status"] == "PASS" for row in case_results),
        "all_values_within_tolerance": all_values_close,
        "all_threshold_decisions_match": all_decisions_match,
        "tolerance": {"atol": ATOL, "rtol": RTOL},
        "versions": {"python": sys.version, "platform": platform.platform(), "torch": torch.__version__, "onnx": onnx.__version__, "onnxruntime": ort.__version__, "numpy": np.__version__, "polars": pl.__version__},
        "device": "CPU only",
        "network_access": False,
        "remote_compute": False,
        "labels_opened": False,
        "e014_prediction_seal_sha256": sha(e014_out / "prediction-seal.json"),
        "e014_artifact_manifest_sha256": sha(e014_out / "artifact-manifest.json"),
        "e014_checkpoint_hashes": {case: sha(e014_out / "models" / f"{case}.pt") for case in CASES},
        "telemetry_hashes": telemetry_hashes,
        "cases": case_results,
    }
    (output_dir / "parity.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    parity_hash = sha(output_dir / "parity.json")
    (output_dir / "parity-seal.json").write_text(json.dumps({"run_id": "E015-R001", "parity_sha256": parity_hash, "labels_opened": False}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": result["run_id"], "passed_cases": result["passed_cases"], "all_values_within_tolerance": result["all_values_within_tolerance"], "all_threshold_decisions_match": result["all_threshold_decisions_match"], "onnx_files": sum("onnx_sha256" in row for row in case_results)}, indent=2))
    if result["passed_cases"] != len(CASES):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
