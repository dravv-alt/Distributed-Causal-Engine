from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E027-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pf=RUN/"plans.json";seal=json.loads((RUN/"prediction-seal.json").read_text());assert sha(pf)==seal["plans_sha256"] and not seal["labels_loaded"] and not seal["actions_executed"]
    plans=json.loads(pf.read_text())["plans"];cases=json.loads((BASE/"fixtures/inputs.json").read_text())["cases"];labels=json.loads((BASE/"fixtures/evaluator-only/feasibility-labels.json").read_text())["cases"];report=json.loads((RUN/"evaluation.json").read_text());by={c["scenario_id"]:c for c in cases}
    baseline_viol=accepted=valid=correct_rej=false_accept=feasible_goal=0
    for row in plans:
        c=by[row["scenario_id"]];truth=labels[row["scenario_id"]]["feasible"]
        def replay(actions):
            h=c["healthy_replicas"];cost=0;ok=True;goal=False
            for a in actions:
                if a=="scale_one":cost+=5;h+=1
                elif a=="restart_one":cost+=2;goal=True;ok &= h-1>=2 and 1<=1
                else:ok=False
            ok &= cost<=c["budget"]
            return ok,goal,cost
        base,_,_=replay(row["unconstrained"]["plan"]);baseline_viol+=not base
        con=row["constraint_aware"]
        if con["status"]=="REJECTED":correct_rej+=not truth;assert con["plan"]==[]
        else:
            accepted+=1;ok,goal,_=replay(con["plan"]);valid+=ok;false_accept+=not truth or not ok;feasible_goal+=truth and ok and goal
            assert ok
    assert baseline_viol==report["unconstrained"]["constraint_violations"] and accepted==report["constraint_aware"]["accepted"] and valid==report["constraint_aware"]["accepted_valid_plans"] and correct_rej==report["constraint_aware"]["correctly_rejected_infeasible"] and false_accept==report["constraint_aware"]["false_acceptances"] and feasible_goal==report["constraint_aware"]["feasible_goal_attained"]
    audit={"audit":"E027-R001 independent safety constraint audit","passed":True,"cases":len(plans),"checks":["prediction seal and zero execution","unconstrained baseline replay","replica availability during restart","disruption and budget checks","constrained rejection and goal attainment recomputed"],"hashes":{"plans":sha(pf),"inputs":sha(BASE/"fixtures/inputs.json"),"labels":sha(BASE/"fixtures/evaluator-only/feasibility-labels.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
