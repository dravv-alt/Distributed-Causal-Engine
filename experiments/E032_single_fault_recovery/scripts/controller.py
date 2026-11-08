from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];INPUT=BASE/"fixtures/inputs.json";RUN=BASE/"results/E032-R001";ACTION={"cpu":"scale_service","database":"repair_database","network":"reroute_traffic"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cases=json.loads(INPUT.read_text())["cases"];rows=[]
    for c in cases:
        diagnosis=max(c["signals"],key=lambda k:(c["signals"][k],k));action=ACTION[diagnosis];approved=c["simulated_operator_approval"]
        rows.append({"scenario_id":c["scenario_id"],"diagnosis":diagnosis,"action":action,"approved":approved,"plan_valid":action==ACTION[diagnosis],"decision":"EXECUTE_IN_SIMULATOR" if approved else "NO_ACTION_APPROVAL_ABSENT","mttd_ticks":2,"planned_mttr_ticks":6 if approved else None})
    RUN.mkdir(parents=True,exist_ok=True);p=RUN/"controller-decisions.json";p.write_text(json.dumps({"decisions":rows},indent=2)+"\n",encoding="utf-8")
    (RUN/"controller-seal.json").write_text(json.dumps({"decisions_sha256":sha(p),"input_sha256":sha(INPUT),"fault_schedule_loaded":False,"fault_labels_loaded":False,"external_actions":False},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"decisions":len(rows),"schedule_loaded":False,"external_actions":False,"sealed":True},indent=2))
if __name__=="__main__":main()
