from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E025-R001";ACTIONS=("scale_service","repair_database","reroute_traffic")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pf=RUN/"predictions.json";seal=json.loads((RUN/"prediction-seal.json").read_text())
    if seal["prediction_sha256"]!=sha(pf) or seal["labels_and_outcomes_loaded"] is not False:raise SystemExit("seal invalid")
    rows=json.loads(pf.read_text())["predictions"];lp=BASE/"fixtures/evaluator-only/mechanisms-and-outcomes.json";truth=json.loads(lp.read_text())["cases"]
    if set(truth)!={r["scenario_id"] for r in rows}:raise SystemExit("label coverage mismatch")
    best=pair=total=0;err=[];per_action={a:{"predicted":[],"actual":[]} for a in ACTIONS}
    for r in rows:
        y=truth[r["scenario_id"]]["controlled_recovery"];p=r["predicted_recovery"]
        best+=r["ranking"][0]==max(y,key=lambda a:(y[a],a)); total+=len(ACTIONS)*(len(ACTIONS)-1)//2
        for i,a in enumerate(ACTIONS):
            per_action[a]["predicted"].append(p[a]);per_action[a]["actual"].append(y[a]);err.append(abs(p[a]-y[a]))
            for b in ACTIONS[i+1:]:pair+=(p[a]-p[b])*(y[a]-y[b])>0
    action_results={a:{"mean_predicted_recovery":float(np.mean(v["predicted"])),"mean_controlled_recovery":float(np.mean(v["actual"])),"mae":float(np.mean(np.abs(np.asarray(v["predicted"])-np.asarray(v["actual"]))))} for a,v in per_action.items()}
    no_action_mae=float(np.mean([abs(x) for v in per_action.values() for x in v["actual"]]))
    result={"experiment":"E025-R001","planning_stage":"XP022","n_cases":len(rows),"best_action_match_rate":best/len(rows),"pairwise_ranking_consistency":pair/total,"mean_absolute_recovery_error":float(np.mean(err)),"no_action_zero_prediction_mae":no_action_mae,"per_action":action_results,"provenance":{"prediction_sha256":sha(pf),"input_sha256":sha(BASE/"fixtures/inputs.json"),"outcome_sha256":sha(lp)},"interpretation":"Synthetic action ranking only; no intervention executed on DCE or a service."}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
