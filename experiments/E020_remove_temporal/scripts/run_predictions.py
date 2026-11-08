from __future__ import annotations
import hashlib,json,platform,sys
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];INPUT=BASE/"fixtures/test-inputs.json";RUN=BASE/"results/E020-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ranks(v):
    ids=sorted(v);o=sorted(ids,key=lambda n:(-v[n],n));r={};i=0
    while i<len(o):
        j=i+1
        while j<len(o) and v[o[j]]==v[o[i]]:j+=1
        s=1-(((i+1)+j)/2-1)/max(1,len(o)-1)
        for n in o[i:j]:r[n]=float(s)
        i=j
    return r
def predict(c):
    ids=[x["service_id"] for x in c["nodes"]];by={x["service_id"]:x for x in c["nodes"]};adj={x:[] for x in ids}
    for a,b in c["edges"]:adj[a].append(b)
    reach={}
    for x in ids:
        seen=set();todo=list(adj[x])
        while todo:
            z=todo.pop()
            if z in seen:continue
            seen.add(z);todo.extend(adj[z])
        reach[x]=seen
    mods={"neural":ranks({x:by[x]["neural_signal"] for x in ids}),"symbolic":ranks({x:by[x]["symbolic_score"] for x in ids}),"topology":ranks({x:float(len(reach[x])) for x in ids}),"temporal":ranks({x:-by[x]["onset"] for x in ids})}
    arms={}
    for arm,use in (("full_fusion",("neural","symbolic","topology","temporal")),("temporal_disabled",("neural","symbolic","topology"))):
        s={x:sum(mods[m][x] for m in use)/len(use) for x in ids};order=sorted(ids,key=lambda x:(-s[x],x));path=[]
        if reach[order[0]]:path=[order[0],max(reach[order[0]],key=lambda x:(by[x]["neural_signal"],x))]
        arms[arm]={"scores":s,"ranking":order,"abstained":s[order[0]]-s[order[1]]<.05,"explanation_path":path}
    return {"scenario_id":c["scenario_id"],"arms":arms}
def main():
    rows=[predict(c) for c in json.loads(INPUT.read_text())["cases"]];RUN.mkdir(parents=True,exist_ok=True);o=RUN/"predictions.json";o.write_text(json.dumps({"predictions":rows},indent=2)+"\n",encoding="utf-8")
    (RUN/"prediction-seal.json").write_text(json.dumps({"prediction_sha256":sha(o),"input_sha256":sha(INPUT),"labels_loaded":False,"network_used":False,"device":"cpu","python":sys.version,"platform":platform.platform(),"numpy":np.__version__},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"predictions":len(rows),"arms":["full_fusion","temporal_disabled"],"temporal_used_in_disabled_scores":False,"labels_loaded":False,"sealed":True},indent=2))
if __name__=="__main__":main()
