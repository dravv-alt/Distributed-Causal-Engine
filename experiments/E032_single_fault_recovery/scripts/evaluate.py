from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E032-R001";FIX=BASE/"fixtures"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    dp=RUN/"controller-decisions.json";seal=json.loads((RUN/"controller-seal.json").read_text())
    if seal["decisions_sha256"]!=sha(dp) or seal["fault_schedule_loaded"] is not False:raise SystemExit("controller seal invalid")
    decisions=json.loads(dp.read_text())["decisions"];outcomes=json.loads((RUN/"sandbox-outcomes.json").read_text())["outcomes"];labels=json.loads((FIX/"evaluator-only/fault-labels.json").read_text())["faults"];ob={x["scenario_id"]:x for x in outcomes}
    correct=sum(d["diagnosis"]==labels[d["scenario_id"]]["true_fault"] for d in decisions);approved=[d for d in decisions if d["approved"]];denied=[d for d in decisions if not d["approved"]];recovered=sum(ob[d["scenario_id"]]["recovered"] for d in decisions);false=sum(ob[d["scenario_id"]]["false_remediation"] for d in approved)
    result={"experiment":"E032-R001","planning_stage":"XP029","cases":len(decisions),"diagnosis_accuracy":correct/len(decisions),"plan_validity":{"valid":sum(d["plan_valid"] for d in decisions),"n":len(decisions)},"simulated_approval":{"approved":len(approved),"declined_without_approval":len(denied),"actions_executed_without_approval":sum(ob[d["scenario_id"]]["action_executed_in_simulator"] for d in denied)},"recovery":{"successful":recovered,"n":len(decisions),"rate":recovered/len(decisions)},"false_remediation":{"count":false,"n_approved":len(approved),"rate":false/len(approved) if approved else None},"logical_time_ticks":{"mttd":sum(d["mttd_ticks"] for d in decisions)/len(decisions),"mttr_for_recovered":6 if recovered else None,"wall_clock_measurement":False},"provenance":{"decisions_sha256":sha(dp),"sandbox_outcomes_sha256":sha(RUN/"sandbox-outcomes.json"),"fault_labels_sha256":sha(FIX/"evaluator-only/fault-labels.json")},"interpretation":"Synthetic closed-loop simulation; not human-approved service recovery."}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
