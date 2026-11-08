from __future__ import annotations
import hashlib,json,platform,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];INPUT=BASE/"fixtures/inputs.json";RUN=BASE/"results/E026-R001"
CONTRACTS=[("repair_database","database_saturated",120),("scale_service","service_overloaded",100),("reroute_traffic","network_congested",80)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def plan(case):
    state=dict(case["state"]);goal=case["goal"]["latency_at_most_ms"];steps=[];used=set()
    while state["latency_ms"]>goal:
        eligible=[(name,pre,delta) for name,pre,delta in CONTRACTS if state[pre] and name not in used]
        if not eligible:break
        name,pre,delta=eligible[0];before=dict(state);state[pre]=False;state["latency_ms"]=max(0.0,state["latency_ms"]-delta);steps.append({"action":name,"precondition":pre,"state_before":before,"state_after":dict(state)});used.add(name)
    return {"scenario_id":case["scenario_id"],"plan":steps,"predicted_final_state":state,"predicted_goal_met":state["latency_ms"]<=goal}
def main():
    cases=json.loads(INPUT.read_text())["cases"];rows=[plan(c) for c in cases];RUN.mkdir(parents=True,exist_ok=True);p=RUN/"plans.json";p.write_text(json.dumps({"plans":rows},indent=2)+"\n",encoding="utf-8")
    (RUN/"prediction-seal.json").write_text(json.dumps({"plans_sha256":sha(p),"input_sha256":sha(INPUT),"evaluator_labels_loaded":False,"execution_performed":False,"network_used":False,"python":sys.version,"platform":platform.platform()},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"plans":len(rows),"actions_executed":0,"labels_loaded":False,"sealed":True},indent=2))
if __name__=="__main__":main()
