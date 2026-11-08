from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E028-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objective(recovery,cost,risk,disruption,reversible):return .45*recovery-.15*(cost/7)-.15*risk-.15*disruption+.10*reversible
def main():
    pf=RUN/"plans.json";seal=json.loads((RUN/"prediction-seal.json").read_text());assert sha(pf)==seal["plans_sha256"] and not seal["actions_executed"]
    rows=json.loads(pf.read_text())["plans"];cases=json.loads((BASE/"fixtures/inputs.json").read_text())["cases"];report=json.loads((RUN/"evaluation.json").read_text());by={x["scenario_id"]:x for x in cases};matches=multi=0;freq={"restart_one":0,"scale_one_then_restart":0,"none":0};selected_u=[];min_u=[]
    for r in rows:
        c=by[r["scenario_id"]];expected=[]
        if c["healthy_replicas"]>=3 and c["budget"]>=2:expected.append(("restart_one",.65,2,.25,1,.8))
        if c["healthy_replicas"]>=2 and c["budget"]>=7:expected.append(("scale_one_then_restart",.85,7,.12,1,.9))
        assert len(r["candidates"])==len(expected)
        calculated=[]
        for n,rec,cost,risk,d,rev in expected:
            u=objective(rec,cost,risk,d,rev);published=next(x for x in r["candidates"] if x["name"]==n);assert abs(u-published["utility"])<1e-12;calculated.append((n,u,cost))
        assert r["selected"]==(max(calculated,key=lambda x:(x[1],x[0]))[0] if calculated else None)
        if len(calculated)>1:multi+=1
        if calculated:
            matches+=r["selected"]==max(calculated,key=lambda x:(x[1],x[0]))[0];chosen=next(x for x in calculated if x[0]==r["selected"]);cheap=min(calculated,key=lambda x:(x[2],x[0]));selected_u.append(chosen[1]);min_u.append(cheap[1]);freq[r["selected"]]+=1
        else:freq["none"]+=1
    assert matches==report["selected_matches_exhaustive_maximum"] and multi==report["multiple_alternative_cases"] and freq==report["selected_action_plan_frequency"]
    gain=sum(a-b for a,b in zip(selected_u,min_u))/len(selected_u);assert abs(gain-report["mean_utility_gain_vs_minimum_cost_plan"])<1e-12
    audit={"audit":"E028-R001 independent objective enumeration","passed":True,"cases":len(rows),"checks":["plan seal and no action execution","candidate feasibility rebuilt from initial state","each candidate utility independently recalculated","selected alternative matches exhaustive maximum","minimum-cost comparison recalculated"],"hashes":{"plans":sha(pf),"inputs":sha(BASE/"fixtures/inputs.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
