"""Independent read-only recomputation audit for E006-R002."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "E006_rcaeval_feature_coverage"
RUN = EXP / "results" / "E006-R002"
INPUT_ROOT = ROOT / "data" / "rcaeval" / "inference"
CONFIG = json.loads((EXP / "configuration-r002.json").read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    result = json.loads((RUN / "feature-scan.json").read_text(encoding="utf-8"))
    provenance = json.loads((RUN / "source-manifest-r002.json").read_text(encoding="utf-8"))
    expected_cases = set(CONFIG["blind_case_ids"])
    scanned = {row["relative_path"]: row for row in result["per_file"]}
    discovered = {
        (INPUT_ROOT / case / f"{modality}.parquet").relative_to(ROOT).as_posix()
        for case, modalities in CONFIG["expected_modalities_by_case"].items()
        for modality in modalities
    }
    checks: dict[str, bool] = {
        "summary_complete_status": result.get("status") == "COMPLETED_DESCRIPTIVE_LOCAL_CORPUS_SCAN",
        "exact_frozen_case_set": set(result.get("frozen_case_ids", [])) == expected_cases,
        "expected_case_count": result.get("case_count") == len(expected_cases) == 9,
        "expected_file_count": result.get("parquet_file_count") == CONFIG["expected_parquet_file_count"] == 19,
        "expected_local_file_set": set(scanned) == discovered,
        "only_inference_paths": all(path.startswith("data/rcaeval/inference/") for path in scanned),
        "evaluator_only_not_read": provenance.get("evaluator_only_read") is False,
        "no_network": provenance.get("network_access") is False,
        "feature_union_recomputed": False,
        "feature_intersection_recomputed": False,
        "file_metadata_and_null_counts_match": False,
        "source_hashes_match": False,
    }

    feature_sets: dict[str, set[str]] = {}
    feature_presence: dict[str, int] = {}
    metadata_ok = True
    input_hashes_ok = True
    per_case_expected = CONFIG["expected_modalities_by_case"]
    for case in CONFIG["blind_case_ids"]:
        actual_modalities = {p.stem for p in (INPUT_ROOT / case).glob("*.parquet")}
        if actual_modalities != set(per_case_expected[case]):
            metadata_ok = False
        metric_path = INPUT_ROOT / case / "metrics.parquet"
        metric_table = pq.read_table(metric_path)
        fields = set(metric_table.schema.names) - {"time"}
        feature_sets[case] = fields
        metric_record = scanned.get(metric_path.relative_to(ROOT).as_posix())
        if metric_record is None:
            metadata_ok = False
            continue
        if metric_record["row_count"] != metric_table.num_rows or metric_record["column_count"] != metric_table.num_columns:
            metadata_ok = False
        recorded_nulls = {f["name"]: f["top_level_null_count"] for f in metric_record["fields"]}
        actual_nulls = {
            field.name: int(metric_table.column(i).combine_chunks().null_count)
            for i, field in enumerate(metric_table.schema)
        }
        if recorded_nulls != actual_nulls:
            metadata_ok = False
        metric_columns = metric_table.schema.names
        if len(metric_columns) != len(set(metric_columns)) or "time" not in metric_columns:
            metadata_ok = False

    all_files_metadata_ok = True
    for relative, record in scanned.items():
        path = ROOT / Path(relative)
        if not path.is_file() or path.stat().st_size != record["bytes"]:
            all_files_metadata_ok = False
            input_hashes_ok = False
            continue
        actual_hash = sha(path)
        if actual_hash != record["sha256"]:
            input_hashes_ok = False
        if provenance.get("input_sha256", {}).get(relative) != actual_hash:
            input_hashes_ok = False
        table = pq.read_table(path)
        actual_fields = [
            {"name": field.name, "arrow_type": str(field.type),
             "top_level_null_count": int(table.column(i).combine_chunks().null_count)}
            for i, field in enumerate(table.schema)
        ]
        recorded_fields = [
            {"name": f["name"], "arrow_type": f["arrow_type"],
             "top_level_null_count": f["top_level_null_count"]}
            for f in record["fields"]
        ]
        if record["row_count"] != table.num_rows or record["column_count"] != table.num_columns or actual_fields != recorded_fields:
            all_files_metadata_ok = False

    union = set.union(*feature_sets.values())
    intersection = set.intersection(*feature_sets.values())
    for name in union:
        feature_presence[name] = sum(name in feature_sets[case] for case in CONFIG["blind_case_ids"])
    checks["feature_union_recomputed"] = sorted(union) == result.get("feature_union")
    checks["feature_intersection_recomputed"] = sorted(intersection) == result.get("feature_intersection")
    checks["feature_presence_recomputed"] = feature_presence == result.get("feature_case_presence_count")
    checks["file_metadata_and_null_counts_match"] = metadata_ok and all_files_metadata_ok
    checks["source_hashes_match"] = input_hashes_ok and len(provenance.get("input_sha256", {})) == len(discovered)

    audit = {
        "run_id": CONFIG["run_id"],
        "audit_type": "independent read-only Parquet metadata/hash recomputation; not human review",
        "checks": checks,
        "pass": all(checks.values()),
        "files_recomputed": len(scanned),
        "cases_recomputed": len(feature_sets),
        "feature_union_count": len(union),
        "feature_intersection_count": len(intersection),
        "limitations": [
            "This verifies the local nine-case scan only, not the full RCAEval corpus.",
            "It verifies structural coverage, not field semantics, units, alignment validity, or RCA quality."
        ],
    }
    out = RUN / "independent-audit-r002.json"
    with out.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(audit, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(audit, indent=2))
    return 0 if audit["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
