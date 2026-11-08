from __future__ import annotations
import hashlib,json,platform,sys
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1]; INPUT=BASE/"fixtures/test-inputs.json"; RUN=BASE/"results/E019-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ranks(v):
    ids=sorted(v); order=sorted(ids,key=lambda n:(-v[n],n)); out={}; i=0
    while i<len(order):
        j=i+1
        while j<len(order) and v[order[j]]==v[order[i]]:j+=1
        s=1-(((i+1)+j)/2-1)/max(1,len(order)-1)
        for n in order[i:j]:out[n]=float(s)
        i=j
    return out
def predict(c):
    ids=[n["service_id"] for n in c["nodes"]]; by={n["service_id"]:n for n in c["nodes"]}; adj={n:[] for n in ids}
    for a,b in c["edges"]:adj[a].append(b)
    reach={}
    for n in ids:
        seen=set(); todo=list(adj[n])
        while todo:
            x=todo.pop()
            if x in seen:continue
            seen.add(x);todo.extend(adj[x])
        reach[n]=seen
    mods={"neural":ranks({n:by[n]["neural_signal"] for n in ids}),"symbolic":ranks({n:by[n]["symbolic_score"] for n in ids}),"temporal":ranks({n:-by[n]["onset"] for n in ids}),"topology":ranks({n:float(len(reach[n])) for n in ids})}
    arms={}
    for arm,use in (("full_fusion",("neural","symbolic","temporal","topology")),("topology_disabled",("neural","symbolic","temporal"))):
        scores={n:sum(mods[m][n] for m in use)/len(use) for n in ids}; ranking=sorted(ids,key=lambda x:(-scores[x],x)); path=[]
        if arm=="full_fusion" and reach[ranking[0]]:path=[ranking[0],max(reach[ranking[0]],key=lambda x:(by[x]["neural_signal"],x))]
        arms[arm]={"ranking":ranking,"scores":scores,"abstained":scores[ranking[0]]-scores[ranking[1]]<.05,"explanation_path":path}
    return {"scenario_id":c["scenario_id"],"arms":arms}
def main():
    cases=json.loads(INPUT.read_text())["cases"]; rows=[predict(c) for c in cases]; RUN.mkdir(parents=True,exist_ok=True); out=RUN/"predictions.json"
    out.write_text(json.dumps({"predictions":rows},indent=2)+"\n",encoding="utf-8")
    (RUN/"prediction-seal.json").write_text(json.dumps({"prediction_sha256":sha(out),"input_sha256":sha(INPUT),"labels_loaded":False,"network_used":False,"device":"cpu","python":sys.version,"platform":platform.platform(),"numpy":np.__version__},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"predictions":len(rows),"arms":["full_fusion","topology_disabled"],"topology_used_in_disabled_scores":False,"labels_loaded":False,"sealed":True},indent=2))
if __name__=="__main__":main()
