from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E030-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pf=RUN/"transitions.json";seal=json.loads((RUN/"prediction-seal.json").read_text())
    if seal["transitions_sha256"]!=sha(pf) or seal["external_actions"] is not False:raise SystemExit("seal invalid")
    rows=json.loads(pf.read_text())["transitions"];inputs=json.loads((BASE/"fixtures/inputs.json").read_text())["cases"];by={x["scenario_id"]:x for x in inputs};per={a:{"n":0,"exact_matches":0,"invariant_preserved":0} for a in ("restart","scale","reroute","rollback")}
    for r in rows:
        c=by[r["scenario_id"]];a=r["action"];p=r["predicted_state"];o=r["observed_state"];per[a]["n"]+=1;per[a]["exact_matches"]+=p==o
        valid=o["healthy_replicas"]<=o["replicas"]
        if a=="restart":valid &= o["replicas"]==c["initial_state"]["replicas"] and o["healthy_replicas"]==c["initial_state"]["healthy_replicas"]
        elif a=="scale":valid &= o["replicas"]==c["initial_state"]["replicas"]+1 and o["healthy_replicas"]==c["initial_state"]["healthy_replicas"]+1
        elif a=="reroute":valid &= o["route"]==c["arguments"]["target"]
        else:valid &= o==c["arguments"]["snapshot_state"]
        per[a]["invariant_preserved"]+=bool(valid)
    result={"experiment":"E030-R001","planning_stage":"XP027","transitions":len(rows),"exact_state_matches":sum(x["exact_match"] for x in rows),"per_action":per,"rollback_exact_restores":per["rollback"]["invariant_preserved"],"external_actions":False,"provenance":{"transitions_sha256":sha(pf),"input_sha256":sha(BASE/"fixtures/inputs.json")},"interpretation":"In-memory simulator agreement only; no application action integration evidence."}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
