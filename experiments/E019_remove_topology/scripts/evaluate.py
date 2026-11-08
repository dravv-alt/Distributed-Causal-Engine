from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1]; RUN=BASE/"results/E019-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wilson(x,n):
    z=1.959963984540054;p=x/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [float(c-h),float(c+h)]
def metrics(rows,labels,arm):
    ranks=[]; abst=false=expl=pathok=top3=0
    for r in rows:
        a=r["arms"][arm]; y=labels[r["scenario_id"]]; rank=a["ranking"].index(y["root"])+1;ranks.append(rank);top3+=rank<=3;abst+=a["abstained"];false+=(rank!=1 and not a["abstained"]);p=a["explanation_path"];expl+=bool(p);pathok+=bool(p and p[0]==y["root"] and p[1] in y["affected_descendants"])
    n=len(rows);h=sum(x==1 for x in ranks);cov=n-abst
    return {"n":n,"top1":h/n,"top1_wilson95":wilson(h,n),"top3":top3/n,"mrr":float(np.mean([1/x for x in ranks])),"false_diagnosis_rate_nonabstained":false/cov if cov else None,"abstention_rate":abst/n,"coverage":cov/n,"explanation_coverage":expl/n,"path_accuracy_among_cases":pathok/n,"path_accuracy_when_explained":pathok/expl if expl else None}
def main():
    p=RUN/"predictions.json";seal=json.loads((RUN/"prediction-seal.json").read_text())
    if seal["prediction_sha256"]!=sha(p) or seal["labels_loaded"] is not False:raise SystemExit("seal invalid")
    rows=json.loads(p.read_text())["predictions"]; lp=BASE/"fixtures/evaluator-only/test-labels.json";labels=json.loads(lp.read_text())["case_labels"]
    if set(labels)!={x["scenario_id"] for x in rows}:raise SystemExit("label coverage mismatch")
    scores={a:metrics(rows,labels,a) for a in ("full_fusion","topology_disabled")}
    y0=np.array([r["arms"]["full_fusion"]["ranking"][0]==labels[r["scenario_id"]]["root"] for r in rows],dtype=np.int8);y1=np.array([r["arms"]["topology_disabled"]["ranking"][0]==labels[r["scenario_id"]]["root"] for r in rows],dtype=np.int8)
    m0=np.array([1/(r["arms"]["full_fusion"]["ranking"].index(labels[r["scenario_id"]]["root"])+1) for r in rows]);m1=np.array([1/(r["arms"]["topology_disabled"]["ranking"].index(labels[r["scenario_id"]]["root"])+1) for r in rows])
    rng=np.random.default_rng(19016);ix=rng.integers(0,len(rows),size=(10000,len(rows)));dt=(y1[ix].mean(1)-y0[ix].mean(1));dm=(m1[ix].mean(1)-m0[ix].mean(1))
    result={"experiment":"E019-R001","planning_stage":"XP016","dataset":"synthetic fresh-seed cases","metrics":scores,"paired_topology_disabled_minus_full":{"top1_difference":float(y1.mean()-y0.mean()),"top1_bootstrap95":[float(np.quantile(dt,.025)),float(np.quantile(dt,.975))],"mrr_difference":float(m1.mean()-m0.mean()),"mrr_bootstrap95":[float(np.quantile(dm,.025)),float(np.quantile(dm,.975))],"replicates":10000,"seed":19016},"provenance":{"prediction_sha256":sha(p),"input_sha256":sha(BASE/"fixtures/test-inputs.json"),"label_sha256":sha(lp)},"interpretation":"Synthetic topology ablation only; no DCE or RCAEval evidence."}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
