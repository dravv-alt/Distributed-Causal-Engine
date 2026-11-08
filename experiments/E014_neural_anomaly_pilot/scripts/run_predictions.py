from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import polars as pl
import torch
from torch import nn


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E014_neural_anomaly_pilot"
CASE_IDS = ["blind-case-0002", "blind-case-0003", "blind-case-0004", "blind-case-0005", "blind-case-0006", "blind-case-0007", "blind-case-0008", "blind-case-0009", "RE2-TT-case-0001"]
FIT_FRACTION = 0.35
CALIBRATION_END_FRACTION = 0.50
QUANTILE = 0.95
SEED = 17


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
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


def preprocess(matrix: np.ndarray, fit_end: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    train = matrix[:fit_end]
    with np.errstate(all="ignore"):
        med = np.nanmedian(train, axis=0)
    med = np.where(np.isfinite(med), med, 0.0)
    filled = np.where(np.isfinite(matrix), matrix, med)
    with np.errstate(all="ignore"):
        center = np.nanmedian(train, axis=0)
        mad = np.nanmedian(np.abs(train - center), axis=0)
    center = np.where(np.isfinite(center), center, 0.0)
    scale = 1.4826 * mad
    scale = np.where(np.isfinite(scale) & (scale > 0), scale, 1.0)
    standardized = np.clip((filled - center) / scale, -10.0, 10.0).astype(np.float32)
    observed = np.isfinite(matrix)
    missing = (~observed).astype(np.float32)
    model_input = np.concatenate([standardized, missing], axis=1)
    return standardized, observed, model_input


def main() -> None:
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)
    data_root = ROOT / "data" / "rcaeval" / "inference"
    out = BASE / "results" / "E014-R001"
    models_dir = out / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    rows_out = []
    case_manifest = []
    input_hashes = {}
    for case_index, case_id in enumerate(CASE_IDS):
        path = data_root / case_id / "metrics.parquet"
        if not path.is_file():
            raise SystemExit(f"Missing metrics for frozen case {case_id}")
        input_hashes[path.relative_to(ROOT).as_posix()] = sha(path)
        frame = pl.read_parquet(path)
        features = [c for c in frame.columns if c != "time" and frame.schema[c].is_numeric()]
        if not features:
            raise SystemExit(f"No numeric metric features for {case_id}")
        matrix = frame.select(features).to_numpy().astype(np.float64, copy=False)
        times = frame.get_column("time").to_list()
        n = len(times)
        fit_end = max(2, int(n * FIT_FRACTION))
        calibration_end = max(fit_end + 1, int(n * CALIBRATION_END_FRACTION))
        if calibration_end >= n:
            raise SystemExit(f"No score partition for {case_id}")
        standardized, observed, model_input = preprocess(matrix, fit_end)

        # Independent statistical reference: per-row maximum absolute robust z.
        statistical_scores = np.max(np.where(observed, np.abs(standardized), 0.0), axis=1)
        statistical_threshold = float(np.quantile(statistical_scores[fit_end:calibration_end], QUANTILE))

        torch.manual_seed(SEED + case_index)
        x = torch.from_numpy(model_input)
        model = Autoencoder(input_dim=x.shape[1])
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=0.0001)
        model.train()
        for _ in range(40):
            optimizer.zero_grad(set_to_none=True)
            reconstruction = model(x[:fit_end])
            loss = torch.mean((reconstruction - x[:fit_end]) ** 2)
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            recon = model(x).numpy()
        neural_scores = np.mean((recon - model_input) ** 2, axis=1)
        neural_threshold = float(np.quantile(neural_scores[fit_end:calibration_end], QUANTILE))
        model_path = models_dir / f"{case_id}.pt"
        torch.save(model.state_dict(), model_path)

        for row_idx in range(calibration_end, n):
            rows_out.append({
                "case_id": case_id,
                "row_index": row_idx,
                "time": int(times[row_idx]),
                "statistical_score": float(statistical_scores[row_idx]),
                "statistical_alarm": bool(statistical_scores[row_idx] > statistical_threshold),
                "neural_score": float(neural_scores[row_idx]),
                "neural_alarm": bool(neural_scores[row_idx] > neural_threshold),
            })
        case_manifest.append({
            "case_id": case_id,
            "row_count": n,
            "numeric_feature_count": len(features),
            "fit_rows": fit_end,
            "calibration_rows": calibration_end - fit_end,
            "score_rows": n - calibration_end,
            "statistical_threshold": statistical_threshold,
            "neural_threshold": neural_threshold,
            "model_sha256": sha(model_path),
        })

    prediction_path = out / "predictions.jsonl"
    prediction_path.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows_out), encoding="utf-8")
    for case_id in CASE_IDS:
        p = data_root / case_id / "metrics.parquet"
        if sha(p) != input_hashes[p.relative_to(ROOT).as_posix()]:
            raise SystemExit(f"Input changed while inference ran: {case_id}")
    seal = {
        "run_id": "E014-R001",
        "case_count": len(CASE_IDS),
        "prediction_rows": len(rows_out),
        "predictions_sha256": sha(prediction_path),
        "inference_input_hashes": input_hashes,
        "case_partitions": case_manifest,
        "labels_opened": False,
        "network_access": False,
        "remote_compute": False,
        "environment": {"python": sys.version, "platform": platform.platform(), "numpy": np.__version__, "polars": pl.__version__, "torch": torch.__version__, "device": "cpu"},
        "seed": SEED,
    }
    (out / "prediction-seal.json").write_text(json.dumps(seal, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": seal["run_id"], "case_count": seal["case_count"], "prediction_rows": seal["prediction_rows"], "predictions_sha256": seal["predictions_sha256"], "labels_opened": False}, indent=2))


if __name__ == "__main__":
    main()
