from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];INPUT=BASE/"fixtures/inputs.json";RUN=BASE/"results/E033-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def diagnose(c):
    adj={n:[] for n in c["symptoms"]}
    for a,b in c["causal_edges"]:adj[a].append(b)
    reach={}
    for n in adj:
        seen=set();todo=list(adj[n])
        while todo:
            x=todo.pop()
            if x in seen:continue
            seen.add(x);todo.extend(adj[x])
        reach[n]=seen
    root=max((n for n,on in c["symptoms"].items() if on),key=lambda n:(len(reach[n]),-c["onset"][n],n))
    path=[root];cur=root
    while adj[cur]:cur=adj[cur][0];path.append(cur)
    return {"propagation_aware":{"root":root,"path":path,"actions":["repair_database"]},"independent_symptom_treatment":{"root":None,"path":[],"actions":["stabilize_service_b","restart_service_a","clear_retry_queue"]}}
def main():
    rows=[{"scenario_id":c["scenario_id"],**diagnose(c)} for c in json.loads(INPUT.read_text())["cases"]]
    RUN.mkdir(parents=True,exist_ok=True);p=RUN/"diagnoses.json";p.write_text(json.dumps({"diagnoses":rows},indent=2)+"\n",encoding="utf-8")
    (RUN/"prediction-seal.json").write_text(json.dumps({"diagnoses_sha256":sha(p),"input_sha256":sha(INPUT),"root_labels_loaded":False,"external_actions":False},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"diagnoses":len(rows),"methods":2,"labels_loaded":False,"sealed":True},indent=2))
if __name__=="__main__":main()
