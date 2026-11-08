from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E027-R001";MIN=2;MAX_DISRUPTION=1;BUDGET=7
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(plan,initial,budget):
    healthy=initial;cost=0;ok=True;maxd=0;goal=False
    for action in plan:
        if action=="scale_one":
            cost+=5;healthy+=1
        elif action=="restart_one":
            cost+=2;disruption=1;maxd=max(maxd,disruption)
            if healthy-disruption<MIN or disruption>MAX_DISRUPTION:ok=False
            goal=True
        else:ok=False
    if cost>budget:ok=False
    return {"valid":ok,"cost":cost,"max_disruption":maxd,"goal_met":goal,"final_healthy":healthy}
def main():
    pp=RUN/"plans.json";seal=json.loads((RUN/"prediction-seal.json").read_text())
    if seal["plans_sha256"]!=sha(pp) or seal["labels_loaded"] is not False:raise SystemExit("seal invalid")
    plans=json.loads(pp.read_text())["plans"];inputs=json.loads((BASE/"fixtures/inputs.json").read_text())["cases"];labels=json.loads((BASE/"fixtures/evaluator-only/feasibility-labels.json").read_text())["cases"];by={x["scenario_id"]:x for x in inputs}
    base_violations=constrained_valid=reject_correct=false_accept=feasible_accept=0
    for row in plans:
        case=by[row["scenario_id"]];truth=labels[row["scenario_id"]]["feasible"]
        base=check(row["unconstrained"]["plan"],case["healthy_replicas"],case["budget"])
        con=row["constraint_aware"]
        if not base["valid"]:base_violations+=1
        if con["status"]=="REJECTED":reject_correct+=not truth
        else:
            checked=check(con["plan"],case["healthy_replicas"],case["budget"])
            constrained_valid+=checked["valid"]
            feasible_accept+=truth and checked["valid"] and checked["goal_met"]
            false_accept+=not truth or not checked["valid"]
    result={"experiment":"E027-R001","planning_stage":"XP024","cases":len(plans),"unconstrained":{"constraint_violations":base_violations,"n":len(plans)},"constraint_aware":{"accepted_valid_plans":constrained_valid,"accepted":sum(x["constraint_aware"]["status"]=="ACCEPTED" for x in plans),"correctly_rejected_infeasible":reject_correct,"false_acceptances":false_accept,"feasible_goal_attained":feasible_accept},"constraints":{"minimum_healthy_replicas":MIN,"maximum_disruption":MAX_DISRUPTION,"budget":BUDGET},"execution_performed":False,"provenance":{"plans_sha256":sha(pp),"input_sha256":sha(BASE/"fixtures/inputs.json"),"feasibility_label_sha256":sha(BASE/"fixtures/evaluator-only/feasibility-labels.json")},"interpretation":"Synthetic safety constraint verification only; no runtime action safety claim."}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
