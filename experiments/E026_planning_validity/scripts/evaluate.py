from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E026-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pp=RUN/"plans.json";seal=json.loads((RUN/"prediction-seal.json").read_text())
    if seal["plans_sha256"]!=sha(pp) or seal["evaluator_labels_loaded"] is not False:raise SystemExit("plan seal invalid")
    plans=json.loads(pp.read_text())["plans"];labels=json.loads((BASE/"fixtures/evaluator-only/reachability-labels.json").read_text())["cases"]
    inputs=json.loads((BASE/"fixtures/inputs.json").read_text())["cases"];by={c["scenario_id"]:c for c in inputs};contracts={"repair_database":("database_saturated",120),"scale_service":("service_overloaded",100),"reroute_traffic":("network_congested",80)}
    valid=0
    for plan in plans:
        state=dict(by[plan["scenario_id"]]["state"]);seen=set();ok=True
        for step in plan["plan"]:
            action=step["action"]
            if action not in contracts or action in seen:ok=False;break
            pre,delta=contracts[action]
            if not state[pre] or step["precondition"]!=pre or step["state_before"]!=state:ok=False;break
            state[pre]=False;state["latency_ms"]=max(0.0,state["latency_ms"]-delta);seen.add(action)
            if step["state_after"]!=state:ok=False;break
        if state!=plan["predicted_final_state"] or (state["latency_ms"]<=by[plan["scenario_id"]]["goal"]["latency_at_most_ms"])!=plan["predicted_goal_met"]:ok=False
        valid+=ok
    feasible=[p for p in plans if labels[p["scenario_id"]]["reachable"]]
    attained=sum(p["predicted_goal_met"] for p in feasible)
    false_plans=sum(p["predicted_goal_met"] and not labels[p["scenario_id"]]["reachable"] for p in plans)
    missed=sum(not p["predicted_goal_met"] and labels[p["scenario_id"]]["reachable"] for p in plans)
    result={"experiment":"E026-R001","planning_stage":"XP023","cases":len(plans),"plan_validity":{"all_steps_precondition_and_effect_valid":valid,"n":len(plans)},"goal_attainment":{"reachable_cases_attained":attained,"reachable_cases":len(feasible),"rate":attained/len(feasible) if feasible else None,"false_goal_claims_on_unreachable":false_plans,"missed_reachable_goals":missed},"plan_lengths":{"mean":sum(len(p["plan"]) for p in plans)/len(plans),"empty":sum(not p["plan"] for p in plans)},"provenance":{"plans_sha256":sha(pp),"input_sha256":sha(BASE/"fixtures/inputs.json"),"reachability_labels_sha256":sha(BASE/"fixtures/evaluator-only/reachability-labels.json")},"interpretation":"Offline synthetic state/action model validation only."}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
