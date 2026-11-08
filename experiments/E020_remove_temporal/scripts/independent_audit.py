from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E020-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ranks(v):
    ids=sorted(v);o=sorted(ids,key=lambda n:(-v[n],n));r={};i=0
    while i<len(o):
        j=i+1
        while j<len(o) and v[o[j]]==v[o[i]]:j+=1
        s=1-(((i+1)+j)/2-1)/max(1,len(o)-1)
        for n in o[i:j]:r[n]=s
        i=j
    return r
def main():
    pf=RUN/"predictions.json";seal=json.loads((RUN/"prediction-seal.json").read_text());assert sha(pf)==seal["prediction_sha256"] and seal["labels_loaded"] is False
    rows=json.loads(pf.read_text())["predictions"];cases=json.loads((BASE/"fixtures/test-inputs.json").read_text())["cases"];labels=json.loads((BASE/"fixtures/evaluator-only/test-labels.json").read_text())["case_labels"];report=json.loads((RUN/"evaluation.json").read_text());cb={x["scenario_id"]:x for x in cases}
    for row in rows:
        c=cb[row["scenario_id"]];nodes={x["service_id"]:x for x in c["nodes"]};ids=sorted(nodes);adj={x:[] for x in ids}
        for a,b in c["edges"]:adj[a].append(b)
        reach={}
        for x in ids:
            seen=set();todo=list(adj[x])
            while todo:
                z=todo.pop()
                if z in seen:continue
                seen.add(z);todo.extend(adj[z])
            reach[x]=seen
        mods=[ranks({x:nodes[x]["neural_signal"] for x in ids}),ranks({x:nodes[x]["symbolic_score"] for x in ids}),ranks({x:float(len(reach[x])) for x in ids})]
        expected={x:sum(m[x] for m in mods)/3 for x in ids};got=row["arms"]["temporal_disabled"]["scores"]
        assert max(abs(expected[x]-got[x]) for x in ids)<1e-12
    onset=sum(min(c["nodes"],key=lambda x:(x["onset"],x["service_id"]))["service_id"]==labels[c["scenario_id"]]["root"] for c in cases)/len(cases)
    assert abs(onset-report["evaluator_only_onset_consistency"]["earliest_generated_onset_matches_root"])<1e-12
    for arm in ("full_fusion","temporal_disabled"):
        h=t3=ab=false=ex=pk=0;rr=[]
        for row in rows:
            a=row["arms"][arm];y=labels[row["scenario_id"]];rank=a["ranking"].index(y["root"])+1;h+=rank==1;t3+=rank<=3;rr.append(1/rank);ab+=a["abstained"];false+=(rank!=1 and not a["abstained"]);p=a["explanation_path"];ex+=bool(p);pk+=bool(p and p[0]==y["root"] and p[1] in y["affected_descendants"])
        n=len(rows);cov=n-ab;vals={"top1":h/n,"top3":t3/n,"mrr":float(np.mean(rr)),"false_diagnosis_rate_nonabstained":false/cov,"abstention_rate":ab/n,"coverage":cov/n,"explanation_coverage":ex/n,"path_accuracy_among_cases":pk/n,"path_accuracy_when_explained":pk/ex if ex else None}
        for k,v in vals.items():
            pv=report["metrics"][arm][k]
            assert (v is None and pv is None) or abs(v-pv)<1e-12
    audit={"audit":"E020-R001 independent temporal-ablation recomputation","passed":True,"cases":len(rows),"checks":["prediction seal and label separation","temporal-disabled scores recomputed without onset","evaluator-only onset consistency recomputed","both arm localization/abstention/explanation metrics recomputed"],"hashes":{"predictions":sha(pf),"inputs":sha(BASE/"fixtures/test-inputs.json"),"labels":sha(BASE/"fixtures/evaluator-only/test-labels.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
