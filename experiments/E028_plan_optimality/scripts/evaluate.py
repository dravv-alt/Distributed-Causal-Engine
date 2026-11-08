from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E028-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pf=RUN/"plans.json";seal=json.loads((RUN/"prediction-seal.json").read_text())
    if seal["plans_sha256"]!=sha(pf) or seal["actions_executed"] is not False:raise SystemExit("seal invalid")
    rows=json.loads(pf.read_text())["plans"];oracle=0;multi=0;cost=[];selected_u=[];mincost_u=[];freq={"restart_one":0,"scale_one_then_restart":0,"none":0}
    for r in rows:
        cs=r["candidates"]
        if len(cs)>1:multi+=1
        if cs:
            maxu=max(x["utility"] for x in cs);oracle+=abs(next(x["utility"] for x in cs if x["name"]==r["selected"])-maxu)<1e-12
            ch=next(x for x in cs if x["name"]==r["selected"]);cheap=min(cs,key=lambda x:(x["cost"],x["name"]))
            cost.append(ch["cost"]);selected_u.append(ch["utility"]);mincost_u.append(cheap["utility"]);freq[ch["name"]]+=1
        else:freq["none"]+=1
    count=len(rows)
    result={"experiment":"E028-R001","planning_stage":"XP025","cases":count,"feasible_cases":len(cost),"multiple_alternative_cases":multi,"selected_matches_exhaustive_maximum":oracle,"n_with_feasible_alternatives":len(cost),"selected_action_plan_frequency":freq,"mean_selected_cost":sum(cost)/len(cost) if cost else None,"mean_selected_utility":sum(selected_u)/len(selected_u) if selected_u else None,"mean_utility_gain_vs_minimum_cost_plan":sum(a-b for a,b in zip(selected_u,mincost_u))/len(cost) if cost else None,"objective":{"formula":"0.45*recovery - 0.15*(cost/7) - 0.15*risk - 0.15*disruption + 0.10*reversibility","scope":"declared candidate set only"},"provenance":{"plans_sha256":sha(pf),"input_sha256":sha(BASE/"fixtures/inputs.json")},"interpretation":"Exact objective maximization within the synthetic enumerated action set only."}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
