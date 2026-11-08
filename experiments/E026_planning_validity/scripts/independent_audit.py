from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E026-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pf=RUN/"plans.json";seal=json.loads((RUN/"prediction-seal.json").read_text());assert sha(pf)==seal["plans_sha256"] and not seal["evaluator_labels_loaded"] and not seal["execution_performed"]
    plans=json.loads(pf.read_text())["plans"];cases=json.loads((BASE/"fixtures/inputs.json").read_text())["cases"];labels=json.loads((BASE/"fixtures/evaluator-only/reachability-labels.json").read_text())["cases"];report=json.loads((RUN/"evaluation.json").read_text());by={c["scenario_id"]:c for c in cases};effect={"repair_database":("database_saturated",120.0),"scale_service":("service_overloaded",100.0),"reroute_traffic":("network_congested",80.0)}
    valid=0;feasible=attained=falseclaims=missed=0
    for p in plans:
        state=dict(by[p["scenario_id"]]["state"]);seen=set();ok=True
        for step in p["plan"]:
            action=step["action"]
            if action not in effect or action in seen:ok=False;break
            key,delta=effect[action]
            if not state[key] or step["state_before"]!=state or step["precondition"]!=key:ok=False;break
            state[key]=False;state["latency_ms"]=max(0.0,state["latency_ms"]-delta);seen.add(action)
            if step["state_after"]!=state:ok=False;break
        goal=state["latency_ms"]<=by[p["scenario_id"]]["goal"]["latency_at_most_ms"]
        if state!=p["predicted_final_state"] or goal!=p["predicted_goal_met"]:ok=False
        valid+=ok;reachable=labels[p["scenario_id"]]["reachable"]
        feasible+=reachable;attained+=reachable and goal;falseclaims+=goal and not reachable;missed+=reachable and not goal
    assert valid==report["plan_validity"]["all_steps_precondition_and_effect_valid"]
    assert feasible==report["goal_attainment"]["reachable_cases"] and attained==report["goal_attainment"]["reachable_cases_attained"] and falseclaims==report["goal_attainment"]["false_goal_claims_on_unreachable"] and missed==report["goal_attainment"]["missed_reachable_goals"]
    audit={"audit":"E026-R001 independent plan contract audit","passed":True,"cases":len(plans),"checks":["plan seal and no execution","each precondition and state effect replayed independently","final states and goals recomputed","reachability labels used only in evaluator"],"hashes":{"plans":sha(pf),"inputs":sha(BASE/"fixtures/inputs.json"),"labels":sha(BASE/"fixtures/evaluator-only/reachability-labels.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
