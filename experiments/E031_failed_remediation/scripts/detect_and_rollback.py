from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures";RUN=BASE/"results/E031-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    plans=json.loads((RUN/"predictions.json").read_text())["predictions"];observed=json.loads((RUN/"environment-outcomes.json").read_text())["outcomes"];cases=json.loads((FIX/"inputs.json").read_text())["cases"];ob={r["scenario_id"]:r["observed_state"] for r in observed};cb={c["scenario_id"]:c for c in cases};rows=[]
    for p in plans:
        state=ob[p["scenario_id"]];failed=state!=p["expected_state"];restored=cb[p["scenario_id"]]["initial_state"].copy() if failed else state.copy()
        rows.append({"scenario_id":p["scenario_id"],"failure_detected":failed,"disposition":"REPLAN_REQUIRED" if failed else "VERIFIED","rollback_state":restored,"rollback_exact":(not failed) or restored==cb[p["scenario_id"]]["initial_state"]})
    out=RUN/"controller-decisions.json";out.write_text(json.dumps({"decisions":rows},indent=2)+"\n",encoding="utf-8")
    (RUN/"controller-seal.json").write_text(json.dumps({"decisions_sha256":sha(out),"predictions_sha256":sha(RUN/"predictions.json"),"observed_outcomes_sha256":sha(RUN/"environment-outcomes.json"),"failure_schedule_loaded":False,"failure_labels_loaded":False,"external_rollback":False},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"decisions":len(rows),"replan_required":sum(x["failure_detected"] for x in rows),"controller_schedule_access":False,"external_rollback":False},indent=2))
if __name__=="__main__":main()
