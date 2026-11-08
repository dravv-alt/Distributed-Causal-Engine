from __future__ import annotations

import hashlib
import json
from pathlib import Path
import string

import polars as pl


ROOT = Path(__file__).resolve().parents[3]
CASE_IDS = ["RE2-TT-case-0001", *(f"blind-case-{i:04d}" for i in range(2, 10))]
TERMS = ("database", "db", "pool", "saturat", "overload", "exhaust", "latency")
TRANS = str.maketrans({char: " " for char in string.punctuation})


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_tokens(text: str) -> set[str]:
    return set(text.casefold().translate(TRANS).split())


def main() -> None:
    result_path = ROOT / "experiments" / "E011_domain_rule_source_support" / "results" / "E011-R002" / "source-support.json"
    recorded = json.loads(result_path.read_text(encoding="utf-8"))
    terms = {term: {"field_names": 0, "log_messages": 0} for term in TERMS}
    cooccur = {"database_and_saturation_or_overload_same_message": 0, "pool_and_saturation_or_exhaustion_same_message": 0, "metric_fields_with_latency_token": 0}
    hash_ok = True
    for rel, expected in recorded["input_hashes"].items():
        if digest(ROOT / Path(rel)) != expected:
            hash_ok = False
    for case_id in CASE_IDS:
        base = ROOT / "data" / "rcaeval" / "inference" / case_id
        metric = pl.read_parquet(base / "metrics.parquet")
        metric_field_tokens = [split_tokens(str(col)) for col in metric.columns]
        for term in TERMS:
            terms[term]["field_names"] += sum(term in tokens for tokens in metric_field_tokens)
        cooccur["metric_fields_with_latency_token"] += sum("latency" in tokens for tokens in metric_field_tokens)
        logs_path = base / "logs.parquet"
        if logs_path.exists():
            logs = pl.read_parquet(logs_path)
            for message in logs.get_column("message").drop_nulls().to_list():
                tokens = split_tokens(str(message))
                for term in TERMS:
                    terms[term]["log_messages"] += term in tokens
                cooccur["database_and_saturation_or_overload_same_message"] += bool(({"database", "db"} & tokens) and ({"saturation", "saturated", "overload"} & tokens))
                cooccur["pool_and_saturation_or_exhaustion_same_message"] += bool("pool" in tokens and ({"saturation", "saturated", "exhaustion", "exhausted"} & tokens))
    expected_cooccur = recorded["rule_family_availability_counts"]
    expected_terms = recorded["literal_term_counts"]
    passed = hash_ok and terms == expected_terms and cooccur == expected_cooccur
    audit = {
        "run_id": "E011-R002",
        "status": "PASS" if passed else "FAIL",
        "input_hashes_match": hash_ok,
        "term_counts_match": terms == expected_terms,
        "rule_family_counts_match": cooccur == expected_cooccur,
        "independent_tokenizer": "ASCII punctuation translated to spaces; Python set membership",
        "evaluator_root_accessed": False,
        "recomputed_term_counts": terms,
        "recomputed_rule_family_counts": cooccur,
    }
    out = result_path.parent / "independent-audit.json"
    out.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: audit[k] for k in ("status", "input_hashes_match", "term_counts_match", "rule_family_counts_match")}, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
