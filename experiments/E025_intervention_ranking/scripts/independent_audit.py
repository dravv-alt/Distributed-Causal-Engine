from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E025-R001";ACTIONS=("scale_service","repair_database","reroute_traffic")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pf=RUN/"predictions.json";seal=json.loads((RUN/"prediction-seal.json").read_text());assert sha(pf)==seal["prediction_sha256"] and seal["labels_and_outcomes_loaded"] is False
    inputs=json.loads((BASE/"fixtures/inputs.json").read_text())["cases"];rows=json.loads(pf.read_text())["predictions"];truth=json.loads((BASE/"fixtures/evaluator-only/mechanisms-and-outcomes.json").read_text())["cases"];report=json.loads((RUN/"evaluation.json").read_text());ib={x["scenario_id"]:x for x in inputs}
    best=pair=total=0;errs=[];per={a:{"p":[],"y":[]} for a in ACTIONS}
    for r in rows:
        ind=ib[r["scenario_id"]]["indicators"];scores={a:float(np.clip(.10+.75*ind[k]+.05*sum(ind[x] for x in ind if x!=k),0,1)) for a,k in (("scale_service","cpu"),("repair_database","database"),("reroute_traffic","network"))}
        assert all(abs(scores[a]-r["predicted_recovery"][a])<1e-12 for a in ACTIONS)
        assert r["ranking"]==sorted(scores,key=lambda a:(-scores[a],a))
        outcomes=truth[r["scenario_id"]]["controlled_recovery"];best+=r["ranking"][0]==max(outcomes,key=lambda a:(outcomes[a],a))
        for i,a in enumerate(ACTIONS):
            per[a]["p"].append(scores[a]);per[a]["y"].append(outcomes[a]);errs.append(abs(scores[a]-outcomes[a]))
            for b in ACTIONS[i+1:]:pair+=(scores[a]-scores[b])*(outcomes[a]-outcomes[b])>0;total+=1
    assert abs(best/len(rows)-report["best_action_match_rate"])<1e-12 and abs(pair/total-report["pairwise_ranking_consistency"])<1e-12 and abs(np.mean(errs)-report["mean_absolute_recovery_error"])<1e-12
    for a in ACTIONS:
        assert abs(np.mean(per[a]["p"])-report["per_action"][a]["mean_predicted_recovery"])<1e-12
        assert abs(np.mean(per[a]["y"])-report["per_action"][a]["mean_controlled_recovery"])<1e-12
    audit={"audit":"E025-R001 independent action outcome audit","passed":True,"cases":len(rows),"checks":["prediction seal and evaluator separation","all predicted action scores recomputed from inputs","best action and pairwise rankings recomputed","per-action realized outcomes and errors recomputed"],"hashes":{"predictions":sha(pf),"inputs":sha(BASE/"fixtures/inputs.json"),"outcomes":sha(BASE/"fixtures/evaluator-only/mechanisms-and-outcomes.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
