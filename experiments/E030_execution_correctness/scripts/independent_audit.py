from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E030-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def oracle(action,state,args):
    result=state.copy()
    if action=="restart":result["generation"]=result["generation"]+1;result["last_action"]="restart"
    elif action=="scale":result["replicas"]+=1;result["healthy_replicas"]+=1;result["last_action"]="scale"
    elif action=="reroute":result["route"]=args["target"];result["last_action"]="reroute"
    elif action=="rollback":result=args["snapshot_state"].copy()
    else:raise AssertionError(action)
    return result
def main():
    pf=RUN/"transitions.json";seal=json.loads((RUN/"prediction-seal.json").read_text());assert sha(pf)==seal["transitions_sha256"] and not seal["external_actions"]
    rows=json.loads(pf.read_text())["transitions"];inputs=json.loads((BASE/"fixtures/inputs.json").read_text())["cases"];report=json.loads((RUN/"evaluation.json").read_text());by={x["scenario_id"]:x for x in inputs};cnt={a:[0,0] for a in ("restart","scale","reroute","rollback")}
    for r in rows:
        c=by[r["scenario_id"]];expected=oracle(r["action"],c["initial_state"],c["arguments"]);assert expected==r["observed_state"]==r["predicted_state"]
        assert expected["healthy_replicas"]<=expected["replicas"]
        cnt[r["action"]][0]+=1;cnt[r["action"]][1]+=1
        if r["action"]=="rollback":assert expected==c["arguments"]["snapshot_state"]
    assert sum(x["exact_match"] for x in rows)==report["exact_state_matches"]==200
    audit={"audit":"E030-R001 independent transition oracle","passed":True,"transitions":len(rows),"checks":["sealed in-memory-only run","restart, scale, reroute and rollback effects independently replayed","healthy replicas never exceed total replicas","rollback restores snapshot exactly"],"hashes":{"transitions":sha(pf),"inputs":sha(BASE/"fixtures/inputs.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
