from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E019-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ranks(v):
    ids=sorted(v);o=sorted(ids,key=lambda n:(-v[n],n));out={};i=0
    while i<len(o):
        j=i+1
        while j<len(o) and v[o[j]]==v[o[i]]:j+=1
        s=1-(((i+1)+j)/2-1)/max(1,len(o)-1)
        for n in o[i:j]:out[n]=s
        i=j
    return out
def main():
    pf=RUN/"predictions.json";seal=json.loads((RUN/"prediction-seal.json").read_text());assert sha(pf)==seal["prediction_sha256"] and seal["labels_loaded"] is False
    rows=json.loads(pf.read_text())["predictions"];cases=json.loads((BASE/"fixtures/test-inputs.json").read_text())["cases"];labels=json.loads((BASE/"fixtures/evaluator-only/test-labels.json").read_text())["case_labels"];report=json.loads((RUN/"evaluation.json").read_text());cb={c["scenario_id"]:c for c in cases}
    for row in rows:
        c=cb[row["scenario_id"]];nodes={n["service_id"]:n for n in c["nodes"]};ids=sorted(nodes)
        mods=[ranks({n:nodes[n]["neural_signal"] for n in ids}),ranks({n:nodes[n]["symbolic_score"] for n in ids}),ranks({n:-nodes[n]["onset"] for n in ids})]
        expect={n:sum(m[n] for m in mods)/3 for n in ids};got=row["arms"]["topology_disabled"]["scores"]
        assert max(abs(expect[n]-got[n]) for n in ids)<1e-12
        assert row["arms"]["topology_disabled"]["explanation_path"]==[]
    metrics={}
    for arm in ("full_fusion","topology_disabled"):
        hits=top3=abst=false=expl=pathok=0;rr=[]
        for r in rows:
            a=r["arms"][arm];y=labels[r["scenario_id"]];rank=a["ranking"].index(y["root"])+1;hits+=rank==1;top3+=rank<=3;rr.append(1/rank);abst+=a["abstained"];false+=(rank!=1 and not a["abstained"]);p=a["explanation_path"];expl+=bool(p);pathok+=bool(p and p[0]==y["root"] and p[1] in y["affected_descendants"])
        n=len(rows);cov=n-abst;metrics[arm]={"top1":hits/n,"top3":top3/n,"mrr":float(np.mean(rr)),"false_diagnosis_rate_nonabstained":false/cov,"abstention_rate":abst/n,"coverage":cov/n,"explanation_coverage":expl/n,"path_accuracy_among_cases":pathok/n,"path_accuracy_when_explained":pathok/expl if expl else None}
        for k,v in metrics[arm].items():
            published=report["metrics"][arm][k]
            if v is None or published is None: assert v is None and published is None,(arm,k,v,published)
            else: assert abs(v-published)<1e-12,(arm,k,v,published)
    audit={"audit":"E019-R001 independent topology-ablation recomputation","passed":True,"cases":len(rows),"checks":["sealed label-blind predictions","topology-disabled score recomputation using neural/symbolic/temporal features only","no graph path in disabled arm","both arm metric recomputation"],"hashes":{"predictions":sha(pf),"inputs":sha(BASE/"fixtures/test-inputs.json"),"labels":sha(BASE/"fixtures/evaluator-only/test-labels.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
