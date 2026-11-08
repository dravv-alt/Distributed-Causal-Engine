from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures";RUN=BASE/"results/E032-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    decisions=json.loads((RUN/"controller-decisions.json").read_text())["decisions"];faults=json.loads((FIX/"environment-only/fault-schedule.json").read_text())["faults"];rows=[]
    for d in decisions:
        actual=faults[d["scenario_id"]]["true_fault"];executed=d["decision"]=="EXECUTE_IN_SIMULATOR";recovered=executed and d["diagnosis"]==actual
        rows.append({"scenario_id":d["scenario_id"],"action_executed_in_simulator":executed,"recovered":recovered,"false_remediation":executed and not recovered,"remaining_fault":None if recovered else actual})
    out=RUN/"sandbox-outcomes.json";out.write_text(json.dumps({"outcomes":rows},indent=2)+"\n",encoding="utf-8")
    (RUN/"environment-seal.json").write_text(json.dumps({"outcomes_sha256":sha(out),"fault_schedule_sha256":sha(FIX/"environment-only/fault-schedule.json"),"schedule_used_by":"sandbox executor only","controller_loaded_schedule":False,"external_actions":False},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"simulated_outcomes":len(rows),"recovered":sum(x["recovered"] for x in rows),"false_remediations":sum(x["false_remediation"] for x in rows),"external_actions":False},indent=2))
if __name__=="__main__":main()
