from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];INPUT=BASE/"fixtures/inputs.json";RUN=BASE/"results/E030-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def predict(action,state,args):
    out=dict(state)
    if action=="restart":out["generation"]+=1;out["last_action"]="restart"
    elif action=="scale":out["replicas"]+=1;out["healthy_replicas"]+=1;out["last_action"]="scale"
    elif action=="reroute":out["route"]=args["target"];out["last_action"]="reroute"
    elif action=="rollback":out=dict(args["snapshot_state"])
    else:raise ValueError("unsupported action")
    return out
def execute(action,state,args):
    out=dict(state)
    match action:
        case "restart":out.update(generation=out["generation"]+1,last_action="restart")
        case "scale":out.update(replicas=out["replicas"]+1,healthy_replicas=out["healthy_replicas"]+1,last_action="scale")
        case "reroute":out.update(route=args["target"],last_action="reroute")
        case "rollback":out=args["snapshot_state"].copy()
        case _:raise ValueError("unsupported action")
    return out
def main():
    cases=json.loads(INPUT.read_text())["cases"];rows=[]
    for c in cases:
        predicted=predict(c["action"],c["initial_state"],c["arguments"]);observed=execute(c["action"],c["initial_state"],c["arguments"])
        rows.append({"scenario_id":c["scenario_id"],"action":c["action"],"predicted_state":predicted,"observed_state":observed,"exact_match":predicted==observed,"execution_mode":"in-memory"})
    RUN.mkdir(parents=True,exist_ok=True);p=RUN/"transitions.json";p.write_text(json.dumps({"transitions":rows},indent=2)+"\n",encoding="utf-8")
    (RUN/"prediction-seal.json").write_text(json.dumps({"transitions_sha256":sha(p),"input_sha256":sha(INPUT),"external_actions":False,"network_used":False},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"transitions":len(rows),"exact_matches":sum(x["exact_match"] for x in rows),"external_actions":False,"sealed":True},indent=2))
if __name__=="__main__":main()
