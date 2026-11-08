from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RUN = BASE / "results" / "E016-R001"


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    pred_path=RUN/"predictions.json"; seal=json.loads((RUN/"prediction-seal.json").read_text())
    assert sha(pred_path)==seal["prediction_sha256"] and seal["labels_loaded"] is False
    bundle=json.loads(pred_path.read_text()); rows=bundle["predictions"]
    labels=json.loads((BASE/"fixtures/evaluator-only/test-labels.json").read_text())["case_roots"]
    plabels=json.loads((BASE/"fixtures/evaluator-only/permutation-labels.json").read_text())["case_roots"]
    report=json.loads((RUN/"evaluation.json").read_text())
    main=[r for r in rows if not r["scenario_id"].startswith("P-")]
    assert len(main)==300 and len(rows)==400 and set(labels)=={r["scenario_id"] for r in main}
    checks=[]
    for n in (8,12,20):
        subset=[r for r in main if r["n_services"]==n]
        for method in ("fixed_eight","shared_topology"):
            accepted=[r for r in subset if r[method]["status"]=="ACCEPTED"]
            hits1=hits3=0; rr=[]
            for r in accepted:
                ranking=r[method]["ranking"]; root=labels[r["scenario_id"]]
                rank=ranking.index(root)+1
                hits1 += rank==1; hits3 += rank<=3; rr.append(1/rank)
            published=report["main_results_by_service_count"][str(n)][method]
            assert published["n"]==len(accepted)
            assert published["top1"]==(hits1/len(accepted) if accepted else None)
            assert published["top3"]==(hits3/len(accepted) if accepted else None)
            assert published["mrr"]==(sum(rr)/len(accepted) if accepted else None)
            checks.append(f"{n}-service {method}: n/top1/top3/MRR recomputed")
        expect_reject=0 if n==8 else 100
        assert report["main_results_by_service_count"][str(n)]["fixed_rejected"]==expect_reject
        assert report["main_results_by_service_count"][str(n)]["dynamic_rejected"]==0
    perms=[r for r in rows if r["scenario_id"].startswith("P-")]
    assert len(perms)==100 and set(plabels)=={r["scenario_id"] for r in perms}
    original={r["scenario_id"]:r for r in main if r["n_services"]==8}
    for p in perms:
        assert p["fixed_eight"]["status"]!="ACCEPTED"
        assert p["shared_topology"]["ranking"]==original[p["scenario_id"][2:]]["shared_topology"]["ranking"]
    assert len(bundle["malformed_challenges"])==2 and all(x["rejected"] for x in bundle["malformed_challenges"])
    assert report["permutation"]["identical_rankings"]==100
    audit={"audit":"E016-R001 independent label-based recomputation","passed":True,"checks":checks+["membership mismatch counts","100/100 service-order permutations preserve shared-model ranking","2/2 malformed challenge rejection","prediction seal verified"],"input_hashes":{"predictions":sha(pred_path),"test_labels":sha(BASE/"fixtures/evaluator-only/test-labels.json"),"permutation_labels":sha(BASE/"fixtures/evaluator-only/permutation-labels.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n")
    print(json.dumps(audit,indent=2))


if __name__=="__main__": main()
