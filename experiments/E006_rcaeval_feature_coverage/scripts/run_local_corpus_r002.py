"""Complete label-blind scan of all locally available E006 inference Parquet files."""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime
from decimal import Decimal
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "E006_rcaeval_feature_coverage"
RUN = EXP / "results" / "E006-R002"
CONFIG_PATH = EXP / "configuration-r002.json"
PROTOCOL_PATH = EXP / "protocol-amendment-r002.md"
INPUT_ROOT = ROOT / "data" / "rcaeval" / "inference"
CONFIG = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
CASES = CONFIG["blind_case_ids"]
MODALITIES = tuple(CONFIG["allowed_modalities"])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_scalar(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def arrow_json_scalar(value: Any) -> Any:
    return safe_scalar(value.as_py() if hasattr(value, "as_py") else value)


def field_summary(table: pa.Table, index: int, field: pa.Field) -> dict[str, Any]:
    column = table.column(index).combine_chunks()
    result: dict[str, Any] = {
        "name": field.name,
        "arrow_type": str(field.type),
        "top_level_null_count": int(column.null_count),
    }
    if "time" in field.name.casefold() or "timestamp" in field.name.casefold():
        timestamp: dict[str, Any] = {
            "candidate_by_name_only": True,
            "physical_unit_timezone_semantics": "UNKNOWN",
        }
        if not pa.types.is_nested(field.type):
            try:
                timestamp["distinct_non_null_count"] = int(pc.count_distinct(column).as_py())
                timestamp["duplicate_non_null_count"] = max(
                    0, len(column) - int(column.null_count) - timestamp["distinct_non_null_count"]
                )
            except Exception as exc:
                timestamp["distinct_count_status"] = f"UNSUPPORTED:{type(exc).__name__}"
            try:
                bounds = pc.min_max(column).as_py()
                timestamp["raw_min"] = arrow_json_scalar(bounds.get("min"))
                timestamp["raw_max"] = arrow_json_scalar(bounds.get("max"))
            except Exception as exc:
                timestamp["raw_range_status"] = f"UNSUPPORTED:{type(exc).__name__}"
            try:
                values = [v for v in column.to_pylist() if v is not None]
                pairs = list(zip(values, values[1:]))
                timestamp["nondecreasing_in_source_order"] = bool(pairs) and all(a <= b for a, b in pairs)
                timestamp["strictly_increasing_in_source_order"] = bool(pairs) and all(a < b for a, b in pairs)
                timestamp["source_order_comparable_pairs"] = len(pairs)
            except (TypeError, ValueError) as exc:
                timestamp["source_order_status"] = f"UNCOMPARABLE:{type(exc).__name__}"
        else:
            timestamp["comparison_status"] = "SKIPPED_NESTED_TYPE"
        result["timestamp_candidate"] = timestamp
    return result


def scan_file(path: Path, case: str, modality: str) -> tuple[dict[str, Any], pa.Table]:
    before_hash = sha256(path)
    table = pq.read_table(path)
    schema = table.schema
    fields = [field_summary(table, i, schema.field(i)) for i in range(len(schema))]
    after_hash = sha256(path)
    if before_hash != after_hash:
        raise RuntimeError(f"Input changed while scanning: {path.relative_to(ROOT)}")
    row = {
        "case_id": case,
        "modality": modality,
        "relative_path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": before_hash,
        "row_count": int(table.num_rows),
        "column_count": int(table.num_columns),
        "ordered_columns": [field.name for field in schema],
        "fields": fields,
    }
    return row, table


def is_scalar_comparable(field: pa.Field) -> bool:
    return not pa.types.is_nested(field.type) and not pa.types.is_null(field.type)


def timestamp_intersections(
    case: str,
    tables: dict[str, pa.Table],
) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    modality_pairs = (("metrics", "logs"), ("metrics", "traces"), ("logs", "traces"))
    for left_name, right_name in modality_pairs:
        if left_name not in tables or right_name not in tables:
            continue
        left, right = tables[left_name], tables[right_name]
        right_schema = {field.name: field for field in right.schema}
        for left_index, left_field in enumerate(left.schema):
            if not ("time" in left_field.name.casefold() or "timestamp" in left_field.name.casefold()):
                continue
            right_field = right_schema.get(left_field.name)
            if right_field is None or right_field.type != left_field.type:
                continue
            if not is_scalar_comparable(left_field) or not is_scalar_comparable(right_field):
                continue
            left_values = [v for v in left.column(left_index).combine_chunks().to_pylist() if v is not None]
            right_index = right.schema.get_field_index(right_field.name)
            right_values = [v for v in right.column(right_index).combine_chunks().to_pylist() if v is not None]
            try:
                common = set(left_values).intersection(right_values)
            except TypeError:
                continue
            pairs.append({
                "case_id": case,
                "left_modality": left_name,
                "right_modality": right_name,
                "exact_field_name": left_field.name,
                "same_arrow_type": str(left_field.type),
                "unique_raw_value_intersection_count": len(common),
                "left_rows_with_value_in_other_modality": sum(v in common for v in left_values),
                "right_rows_with_value_in_other_modality": sum(v in common for v in right_values),
                "units_timezone_and_clock_equivalence": "UNKNOWN",
            })
    return pairs


def write_json(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def main() -> int:
    RUN.mkdir(parents=True, exist_ok=False)
    expected_cases = set(CASES)
    case_dirs = {case: INPUT_ROOT / case for case in CASES}
    missing_dirs = [case for case, path in case_dirs.items() if not path.is_dir()]
    if missing_dirs:
        write_json(RUN / "failure.json", {"status": "FAIL", "missing_case_directories": missing_dirs})
        raise FileNotFoundError(missing_dirs)

    rows: list[dict[str, Any]] = []
    tables: dict[str, dict[str, pa.Table]] = {case: {} for case in CASES}
    input_paths: list[Path] = []
    try:
        for case in CASES:
            for path in sorted(case_dirs[case].glob("*.parquet")):
                modality = path.stem
                if modality not in MODALITIES:
                    raise ValueError(f"Unexpected direct Parquet modality for {case}: {path.name}")
                if modality in tables[case]:
                    raise ValueError(f"Duplicate modality Parquet for {case}: {modality}")
                row, table = scan_file(path, case, modality)
                rows.append(row)
                tables[case][modality] = table
                input_paths.append(path)
            expected_modalities = set(CONFIG["expected_modalities_by_case"][case])
            if set(tables[case]) != expected_modalities:
                raise ValueError(
                    f"Modality set changed for {case}: expected {sorted(expected_modalities)}, "
                    f"found {sorted(tables[case])}"
                )
        expected_file_count = int(CONFIG["expected_parquet_file_count"])
        if len(rows) != expected_file_count:
            raise ValueError(f"Expected {expected_file_count} Parquet files; found {len(rows)}")
        if set(tables) != expected_cases:
            raise AssertionError("Frozen case set changed")

        metric_fields_by_case: dict[str, set[str]] = {}
        per_case: dict[str, Any] = {}
        for case in CASES:
            table = tables[case].get("metrics")
            feature_fields = set(table.schema.names) - {"time"} if table is not None else set()
            metric_fields_by_case[case] = feature_fields
            files_for_case = [row for row in rows if row["case_id"] == case]
            metric_file = next((x for x in files_for_case if x["modality"] == "metrics"), None)
            metric_nulls = (
                sum(f["top_level_null_count"] for f in metric_file["fields"] if f["name"] != "time")
                if metric_file else None
            )
            metric_feature_cells = metric_file["row_count"] * len(feature_fields) if metric_file else None
            per_case[case] = {
                "available_modalities": sorted(tables[case]),
                "unavailable_modalities": sorted(set(MODALITIES) - set(tables[case])),
                "parquet_file_count": len(files_for_case),
                "metric_row_count": metric_file["row_count"] if metric_file else None,
                "metric_feature_count_excluding_exact_time_column": len(feature_fields) if metric_file else None,
                "metric_feature_cells": metric_feature_cells,
                "metric_feature_top_level_null_cells": metric_nulls,
                "raw_timestamp_intersections": timestamp_intersections(case, tables[case]),
            }

        feature_union = set.union(*(metric_fields_by_case[c] for c in CASES))
        feature_intersection = set.intersection(*(metric_fields_by_case[c] for c in CASES))
        presence = {name: sum(name in metric_fields_by_case[c] for c in CASES) for name in sorted(feature_union)}
        total_rows_by_modality = dict(Counter())
        for row in rows:
            total_rows_by_modality[row["modality"]] = total_rows_by_modality.get(row["modality"], 0) + row["row_count"]

        data = {
            "experiment_id": "E006",
            "run_id": CONFIG["run_id"],
            "planning_stage": "XP003",
            "status": "COMPLETED_DESCRIPTIVE_LOCAL_CORPUS_SCAN",
            "dataset_revision_from_frozen_config": CONFIG["revision"],
            "revision_interpretation": "configuration provenance; raw Parquet files do not self-identify the repository revision",
            "frozen_case_ids": CASES,
            "case_count": len(CASES),
            "parquet_file_count": len(rows),
            "rows_by_modality": total_rows_by_modality,
            "feature_union_count": len(feature_union),
            "feature_intersection_count": len(feature_intersection),
            "feature_union": sorted(feature_union),
            "feature_intersection": sorted(feature_intersection),
            "feature_case_presence_count": presence,
            "per_case": per_case,
            "per_file": rows,
            "semantics": "all measurement units, temporality, aggregation, resets, field meaning, and service identity UNKNOWN without independent metadata",
            "limits": [
                "This scans every locally present inference Parquet file for the nine frozen cases, not the full 735-case corpus.",
                "Absent modalities are local-snapshot availability facts only; no population-wide absence is inferred.",
                "Timestamp-like detection uses field names only; raw min/max and exact overlaps have no unit, timezone, or clock interpretation.",
                "Top-level Arrow null counts do not summarize nested child nulls.",
                "The result measures source-field presence and file coverage, not extractor performance, aligned-window validity, or RCA quality."
            ],
        }
        output_path = RUN / "feature-scan.json"
        write_json(output_path, data)
        git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True).stdout.strip() or "UNKNOWN"
        git_status = subprocess.run(["git", "status", "--short"], cwd=ROOT, text=True, capture_output=True).stdout.splitlines()
        provenance = {
            "run_id": CONFIG["run_id"],
            "execution_mode": "standalone local; OpenResearch not used",
            "command": "python experiments/E006_rcaeval_feature_coverage/scripts/run_local_corpus_r002.py",
            "python": sys.version,
            "platform": platform.platform(),
            "pyarrow": importlib.metadata.version("pyarrow"),
            "orx_path": shutil.which("orx"),
            "git_head": git_head,
            "git_status_excerpt": git_status[:100],
            "network_access": False,
            "evaluator_only_read": False,
            "configuration_sha256": sha256(CONFIG_PATH),
            "protocol_amendment_sha256": sha256(PROTOCOL_PATH),
            "runner_sha256": sha256(Path(__file__)),
            "input_sha256": {p.relative_to(ROOT).as_posix(): sha256(p) for p in sorted(input_paths)},
            "output_sha256": sha256(output_path),
        }
        write_json(RUN / "source-manifest-r002.json", provenance)
        print(json.dumps({
            "run_id": CONFIG["run_id"], "status": data["status"],
            "cases": len(CASES), "files": len(rows), "rows_by_modality": total_rows_by_modality,
            "metric_feature_union": len(feature_union), "metric_feature_intersection": len(feature_intersection),
            "output": str(output_path),
        }, sort_keys=True))
        return 0
    except Exception as exc:
        write_json(RUN / "failure.json", {
            "run_id": CONFIG["run_id"], "status": "FAIL",
            "error": f"{type(exc).__name__}: {exc}",
            "scanned_files_before_failure": [x["relative_path"] for x in rows],
            "input_sha256": {p.relative_to(ROOT).as_posix(): sha256(p) for p in sorted(input_paths)},
        })
        raise


if __name__ == "__main__":
    raise SystemExit(main())
