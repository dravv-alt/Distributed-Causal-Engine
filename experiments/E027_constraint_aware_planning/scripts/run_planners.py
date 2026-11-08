from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];INPUT=BASE/"fixtures/inputs.json";RUN=BASE/"results/E027-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def constrained(c):
    n=c["healthy_replicas"];budget=c["budget"]
    if n>=3 and budget>=2:return {"status":"ACCEPTED","plan":["restart_one"]}
    if n==2 and budget>=7:return {"status":"ACCEPTED","plan":["scale_one","restart_one"]}
    return {"status":"REJECTED","plan":[]}
def main():
    cases=json.loads(INPUT.read_text())["cases"];rows=[]
    for c in cases:rows.append({"scenario_id":c["scenario_id"],"unconstrained":{"status":"PROPOSED","plan":["restart_one"]},"constraint_aware":constrained(c)})
    RUN.mkdir(parents=True,exist_ok=True);p=RUN/"plans.json";p.write_text(json.dumps({"plans":rows},indent=2)+"\n",encoding="utf-8")
    (RUN/"prediction-seal.json").write_text(json.dumps({"plans_sha256":sha(p),"input_sha256":sha(INPUT),"labels_loaded":False,"actions_executed":False,"network_used":False},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"plans":len(rows),"actions_executed":0,"labels_loaded":False,"sealed":True},indent=2))
if __name__=="__main__":main()
