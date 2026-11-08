from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import re
import sys

import polars as pl


ROOT = Path(__file__).resolve().parents[3]
CASE_IDS = ["RE2-TT-case-0001", *(f"blind-case-{i:04d}" for i in range(2, 10))]
TERMS = ("database", "db", "pool", "saturat", "overload", "exhaust", "latency")
TOKENIZER = re.compile(r"[^a-z0-9]+")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def tokens(value: str) -> set[str]:
    return {token for token in TOKENIZER.split(value.casefold()) if token}


def main() -> None:
    data_root = ROOT / "data" / "rcaeval" / "inference"
    files: dict[str, str] = {}
    cases = []
    totals = {term: {"field_names": 0, "log_messages": 0} for term in TERMS}
    family_counts = {
        "database_and_saturation_or_overload_same_message": 0,
        "pool_and_saturation_or_exhaustion_same_message": 0,
        "metric_fields_with_latency_token": 0,
    }
    total_rows = {"metrics": 0, "logs": 0, "traces": 0}

    for case_id in CASE_IDS:
        case_dir = data_root / case_id
        if not case_dir.is_dir():
            raise SystemExit(f"Missing frozen case directory: {case_id}")
        case = {"case_id": case_id, "modalities": {}, "literal_counts": {term: {"field_names": 0, "log_messages": 0} for term in TERMS}}
        for modality in ("metrics", "logs", "traces"):
            path = case_dir / f"{modality}.parquet"
            if not path.exists():
                continue
            rel = path.relative_to(ROOT).as_posix()
            before = sha256(path)
            files[rel] = before
            frame = pl.read_parquet(path)
            cols = [str(c) for c in frame.columns]
            total_rows[modality] += frame.height
            field_tokens = [tokens(c) for c in cols]
            for term in TERMS:
                found = sum(term in row for row in field_tokens)
                case["literal_counts"][term]["field_names"] += found
                totals[term]["field_names"] += found
            data = {"rows": frame.height, "field_count": len(cols)}
            if modality == "metrics":
                latency_fields = [c for c, ts in zip(cols, field_tokens) if "latency" in ts]
                family_counts["metric_fields_with_latency_token"] += len(latency_fields)
                data["latency_field_names"] = latency_fields
            if modality == "logs":
                msg_col = next((c for c in cols if c.casefold() == "message"), None)
                messages = [] if msg_col is None else [str(x) for x in frame.get_column(msg_col).drop_nulls().to_list()]
                db_count = 0
                pool_count = 0
                for message in messages:
                    ts = tokens(message)
                    for term in TERMS:
                        if term in ts:
                            case["literal_counts"][term]["log_messages"] += 1
                            totals[term]["log_messages"] += 1
                    if ({"database", "db"} & ts) and ({"saturation", "saturated", "overload"} & ts):
                        db_count += 1
                    if "pool" in ts and ({"saturation", "saturated", "exhaustion", "exhausted"} & ts):
                        pool_count += 1
                family_counts["database_and_saturation_or_overload_same_message"] += db_count
                family_counts["pool_and_saturation_or_exhaustion_same_message"] += pool_count
                data["messages_with_database_saturation_terms"] = db_count
                data["messages_with_pool_saturation_terms"] = pool_count
            case["modalities"][modality] = data
            if sha256(path) != before:
                raise SystemExit(f"Input changed during scan: {rel}")
        cases.append(case)

    audit_path = ROOT / "src" / "dce_foundation" / "domain.py"
    files[audit_path.relative_to(ROOT).as_posix()] = sha256(audit_path)
    result = {
        "run_id": "E011-R002",
        "protocol_amendment": "protocol-amendment-R002.md",
        "scope": "label-blind token-boundary source-support audit; not rule validation",
        "dataset_revision": "afeacb11bcc94dadfd1c8f483ee4377b2b8b614e",
        "evaluator_root_accessed": False,
        "network_access": False,
        "case_count": len(cases),
        "total_rows": total_rows,
        "literal_term_counts": totals,
        "rule_family_availability_counts": family_counts,
        "cases": cases,
        "input_hashes": dict(sorted(files.items())),
        "environment": {"python": sys.version, "platform": platform.platform(), "polars": pl.__version__},
        "random_seed": None,
        "limitations": [
            "Token presence does not establish signal semantics, truth, or identity.",
            "The log co-occurrence checks are lexical only and are not rule firing evidence.",
            "Latency field names do not establish units, aggregation, health bounds, or an anomaly.",
            "No localization delta or rule/path accuracy can be estimated from this run.",
            "The selected cases are reused from E010 and are not held out.",
        ],
    }
    out = ROOT / "experiments" / "E011_domain_rule_source_support" / "results" / "E011-R002" / "source-support.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": result["run_id"], "case_count": len(cases), "total_rows": total_rows, "literal_term_counts": totals, "rule_family_availability_counts": family_counts, "output": out.relative_to(ROOT).as_posix()}, indent=2))


if __name__ == "__main__":
    main()
