from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];INPUT=BASE/"fixtures/inputs.json";RUN=BASE/"results/E028-R001"
OPTIONS={"restart_one":{"expected_recovery":.65,"cost":2,"risk":.25,"disruption":1,"reversibility":.80,"actions":["restart_one"]},"scale_one_then_restart":{"expected_recovery":.85,"cost":7,"risk":.12,"disruption":1,"reversibility":.90,"actions":["scale_one","restart_one"]}}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def utility(x):return .45*x["expected_recovery"]-.15*(x["cost"]/7)-.15*x["risk"]-.15*x["disruption"]+.10*x["reversibility"]
def main():
    rows=[]
    for c in json.loads(INPUT.read_text())["cases"]:
        feasible=[]
        if c["healthy_replicas"]>=3 and c["budget"]>=2:feasible.append("restart_one")
        if c["healthy_replicas"]>=2 and c["budget"]>=7:feasible.append("scale_one_then_restart")
        candidates=[{"name":n,**OPTIONS[n],"utility":utility(OPTIONS[n])} for n in feasible]
        chosen=max(candidates,key=lambda x:(x["utility"],x["name"]))["name"] if candidates else None
        rows.append({"scenario_id":c["scenario_id"],"candidates":candidates,"selected":chosen})
    RUN.mkdir(parents=True,exist_ok=True);p=RUN/"plans.json";p.write_text(json.dumps({"plans":rows},indent=2)+"\n",encoding="utf-8")
    (RUN/"prediction-seal.json").write_text(json.dumps({"plans_sha256":sha(p),"input_sha256":sha(INPUT),"external_labels_loaded":False,"actions_executed":False,"network_used":False},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(rows),"plans_selected":sum(x["selected"] is not None for x in rows),"actions_executed":0,"sealed":True},indent=2))
if __name__=="__main__":main()
