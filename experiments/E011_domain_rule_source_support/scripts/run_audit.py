from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
import sys

import polars as pl


ROOT = Path(__file__).resolve().parents[3]
CASE_IDS = ["RE2-TT-case-0001", *(f"blind-case-{i:04d}" for i in range(2, 10))]
TERMS = ["database", "db", "pool", "saturat", "overload", "exhaust", "latency", "service"]
RULES = {
    "database_saturation_or_overload": ["database", "db", "saturat", "overload"],
    "connection_pool_saturation_or_exhaustion": ["pool", "saturat", "exhaust"],
    "latency": ["latency"],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def term_counts(texts: list[str]) -> dict[str, int]:
    lowered = [text.casefold() for text in texts]
    return {term: sum(text.count(term) for text in lowered) for term in TERMS}


def main() -> None:
    data_root = ROOT / "data" / "rcaeval" / "inference"
    excluded = ROOT / "data" / "rcaeval" / "evaluator-only"
    if not data_root.is_dir() or not excluded.is_dir():
        raise SystemExit("Expected inference and evaluator-only roots are missing")

    all_hashes: dict[str, str] = {}
    case_results = []
    total_messages: list[str] = []
    total_columns: list[str] = []
    for case_id in CASE_IDS:
        case_dir = data_root / case_id
        if not case_dir.is_dir():
            raise SystemExit(f"Missing frozen case directory: {case_id}")
        entry: dict = {"case_id": case_id, "modalities": {}}
        for name in ("metrics.parquet", "logs.parquet", "traces.parquet", "field-audit.json"):
            path = case_dir / name
            if not path.exists():
                continue
            relative = path.relative_to(ROOT).as_posix()
            before_hash = sha256(path)
            all_hashes[relative] = before_hash
            if path.suffix == ".parquet":
                frame = pl.read_parquet(path)
                columns = [str(c) for c in frame.columns]
                total_columns.extend(columns)
                modality = path.stem
                data = {"rows": frame.height, "columns": columns}
                if modality == "logs":
                    message_col = next((c for c in columns if c.casefold() in {"message", "log", "content"}), None)
                    messages = [] if message_col is None else [str(v) for v in frame.get_column(message_col).drop_nulls().to_list()]
                    total_messages.extend(messages)
                    data["message_field"] = message_col
                    data["message_term_occurrences"] = term_counts(messages)
                entry["modalities"][modality] = data
            else:
                parsed = json.loads(path.read_text(encoding="utf-8"))
                entry["modalities"]["field-audit"] = {
                    "top_level_keys": sorted(parsed) if isinstance(parsed, dict) else []
                }
            after_hash = sha256(path)
            if after_hash != before_hash:
                raise SystemExit(f"Input changed during scan: {relative}")
        case_results.append(entry)

    source = ROOT / "src" / "dce_foundation" / "domain.py"
    source_hash = sha256(source)
    all_hashes[source.relative_to(ROOT).as_posix()] = source_hash
    field_occurrences = term_counts(total_columns)
    log_occurrences = term_counts(total_messages)
    output = {
        "run_id": "E011-R001",
        "scope": "label-blind lexical source-support audit; not rule validation",
        "network_access": False,
        "evaluator_root_accessed": False,
        "dataset_revision": "afeacb11bcc94dadfd1c8f483ee4377b2b8b614e",
        "case_count": len(case_results),
        "cases": case_results,
        "field_name_term_occurrences": field_occurrences,
        "log_message_term_occurrences": log_occurrences,
        "candidate_rule_predicates": RULES,
        "domain_contract_sha256": source_hash,
        "input_hashes": dict(sorted(all_hashes.items())),
        "environment": {"python": sys.version, "platform": platform.platform(), "polars": pl.__version__},
        "random_seed": None,
        "limitations": [
            "Literal word matches do not establish metric/event semantics or truth.",
            "Entity linkage, thresholds, timing semantics, and causal relationships are not inferred.",
            "No localization delta or rule/path accuracy can be estimated from this audit.",
            "The nine cases are selected and reused from E010; they are not held-out.",
        ],
    }
    out_dir = ROOT / "experiments" / "E011_domain_rule_source_support" / "results" / "E011-R001"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "source-support.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": output["run_id"], "cases": output["case_count"], "field_name_term_occurrences": field_occurrences, "log_message_term_occurrences": log_occurrences, "output": str((out_dir / 'source-support.json').relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
