from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures";RUN=BASE/"results/E031-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def apply(c,failed):
    s=c["initial_state"].copy();a=c["action"]
    if a=="restart":
        if failed:s["last_action"]="failed_restart"
        else:s["generation"]+=1;s["last_action"]="restart"
    elif a=="scale":
        s["replicas"]+=1
        if not failed:s["healthy_replicas"]+=1;s["last_action"]="scale"
        else:s["last_action"]="partial_scale"
    elif a=="reroute":
        s["route"]="unexpected-edge" if failed else c["arguments"]["target"];s["last_action"]="failed_reroute" if failed else "reroute"
    return s
def main():
    cases=json.loads((FIX/"inputs.json").read_text())["cases"];plans=json.loads((RUN/"predictions.json").read_text())["predictions"];schedule=json.loads((FIX/"environment-only/failure-schedule.json").read_text())["schedule"]
    by={p["scenario_id"]:p for p in plans};rows=[]
    for c in cases:rows.append({"scenario_id":c["scenario_id"],"observed_state":apply(c,schedule[c["scenario_id"]]["inject_failure"])})
    out=RUN/"environment-outcomes.json";out.write_text(json.dumps({"outcomes":rows},indent=2)+"\n",encoding="utf-8")
    seal={"outcomes_sha256":sha(out),"input_sha256":sha(FIX/"inputs.json"),"prediction_sha256":sha(RUN/"predictions.json"),"environment_schedule_sha256":sha(FIX/"environment-only/failure-schedule.json"),"schedule_used_by":"sandbox executor only","controller_opened_schedule":False}
    (RUN/"environment-seal.json").write_text(json.dumps(seal,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"simulated_outcomes":len(rows),"external_actions":False,"failure_schedule_used_in_executor":True},indent=2))
if __name__=="__main__":main()
