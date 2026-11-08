from __future__ import annotations

import hashlib
import json
from pathlib import Path
import math

BASE = Path(__file__).resolve().parents[1]
RUN = BASE / "results" / "E016-R001"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson(successes, n, z=1.959963984540054):
    if n == 0: return [None, None]
    p = successes / n; d = 1 + z*z/n
    center = (p + z*z/(2*n))/d
    half = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return [center-half, center+half]


def score(rows, labels, method):
    selected = [row for row in rows if row[method]["status"] == "ACCEPTED" and row["scenario_id"] in labels]
    hits1 = hits3 = 0; rr = []
    for row in selected:
        root = labels[row["scenario_id"]]
        ranking = row[method]["ranking"]
        rank = ranking.index(root)+1 if root in ranking else len(ranking)+1
        hits1 += rank == 1; hits3 += rank <= 3; rr.append(1/rank)
    n = len(selected)
    return {"n": n, "top1": hits1/n if n else None, "top1_wilson95": wilson(hits1,n), "top3": hits3/n if n else None, "top3_wilson95": wilson(hits3,n), "mrr": sum(rr)/n if n else None}


def main():
    prediction_path = RUN / "predictions.json"
    seal = json.loads((RUN / "prediction-seal.json").read_text(encoding="utf-8"))
    if seal["prediction_sha256"] != sha(prediction_path) or seal["labels_loaded"] is not False:
        raise SystemExit("prediction seal invalid")
    bundle = json.loads(prediction_path.read_text(encoding="utf-8")); rows = bundle["predictions"]
    labels = json.loads((BASE/"fixtures"/"evaluator-only"/"test-labels.json").read_text(encoding="utf-8"))["case_roots"]
    permutation_labels = json.loads((BASE/"fixtures"/"evaluator-only"/"permutation-labels.json").read_text(encoding="utf-8"))["case_roots"]
    main_rows = [r for r in rows if not r["scenario_id"].startswith("P-")]
    perm_rows = [r for r in rows if r["scenario_id"].startswith("P-")]
    by_size = {}
    for n in (8,12,20):
        current = [r for r in main_rows if r["n_services"] == n]
        by_size[str(n)] = {"fixed_eight": score(current, labels, "fixed_eight"), "shared_topology": score(current, labels, "shared_topology"), "fixed_rejected": sum(r["fixed_eight"]["status"] != "ACCEPTED" for r in current), "dynamic_rejected": sum(r["shared_topology"]["status"] != "ACCEPTED" for r in current)}
    perm_fixed_rejected = sum(r["fixed_eight"]["status"] != "ACCEPTED" for r in perm_rows)
    perm_dynamic = score(perm_rows, permutation_labels, "shared_topology")
    original = {r["scenario_id"]: r for r in main_rows if r["n_services"] == 8}
    permutation_errors=[]; permutation_rank_same=[]
    for r in perm_rows:
        orig = original[r["scenario_id"][2:]]
        a, b = orig["shared_topology"]["scores"], r["shared_topology"]["scores"]
        permutation_errors.extend(abs(a[k]-b[k]) for k in a)
        permutation_rank_same.append(orig["shared_topology"]["ranking"] == r["shared_topology"]["ranking"])
    malformed = bundle["malformed_challenges"]
    result = {"experiment":"E016-R001","planning_stage":"XP013","dataset":"synthetic controlled fixtures","main_results_by_service_count":by_size,"permutation":{"n":len(perm_rows),"fixed_rejected":perm_fixed_rejected,"shared_topology":perm_dynamic,"max_absolute_score_change":max(permutation_errors,default=None),"identical_rankings":sum(permutation_rank_same),"n_rankings":len(permutation_rank_same)},"malformed_challenges":{"n":len(malformed),"rejected":sum(x["rejected"] for x in malformed)},"provenance":{"prediction_sha256":sha(prediction_path),"test_labels_sha256":sha(BASE/"fixtures"/"evaluator-only"/"test-labels.json"),"permutation_labels_sha256":sha(BASE/"fixtures"/"evaluator-only"/"permutation-labels.json")},"interpretation":"Synthetic membership/adaptation pilot only; not RCAEval or real-service evidence."}
    out=RUN/"evaluation.json"; out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__ == "__main__": main()
