from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E033-R001";FIX=BASE/"fixtures"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    dp=RUN/"diagnoses.json";seal=json.loads((RUN/"prediction-seal.json").read_text())
    if seal["diagnoses_sha256"]!=sha(dp) or seal["root_labels_loaded"] is not False:raise SystemExit("seal invalid")
    ds=json.loads(dp.read_text())["diagnoses"];out=json.loads((RUN/"sandbox-outcomes.json").read_text())["outcomes"];labels=json.loads((FIX/"evaluator-only/root-labels.json").read_text())["labels"];ob={x["scenario_id"]:x for x in out};n=len(ds)
    prop_root=sum(d["propagation_aware"]["root"]==labels[d["scenario_id"]]["root"] for d in ds);prop_path=sum(d["propagation_aware"]["path"]==labels[d["scenario_id"]]["propagation_path"] for d in ds)
    result={"experiment":"E033-R001","planning_stage":"XP030","cases":n,"propagation_aware":{"root_accuracy":prop_root/n,"path_accuracy":prop_path/n,"actions_per_case":sum(len(d["propagation_aware"]["actions"]) for d in ds)/n,"first_check_recovery":sum(ob[d["scenario_id"]]["propagation_aware"]["first_check_symptoms_cleared"] for d in ds)/n,"stable_recovery_at_three_checks":sum(ob[d["scenario_id"]]["propagation_aware"]["stable_recovery_after_three_checks"] for d in ds)/n},"independent_symptom_treatment":{"root_separated":sum(d["independent_symptom_treatment"]["root"] is None for d in ds)/n,"actions_per_case":sum(len(d["independent_symptom_treatment"]["actions"]) for d in ds)/n,"first_check_recovery":sum(ob[d["scenario_id"]]["independent_symptom_treatment"]["first_check_symptoms_cleared"] for d in ds)/n,"stable_recovery_at_three_checks":sum(ob[d["scenario_id"]]["independent_symptom_treatment"]["stable_recovery_after_three_checks"] for d in ds)/n,"root_fault_active_at_three_checks":sum(ob[d["scenario_id"]]["independent_symptom_treatment"]["root_fault_active_after_three_checks"] for d in ds)/n},"provenance":{"diagnoses_sha256":sha(dp),"outcomes_sha256":sha(RUN/"sandbox-outcomes.json"),"input_sha256":sha(FIX/"inputs.json"),"root_label_sha256":sha(FIX/"evaluator-only/root-labels.json")},"interpretation":"Synthetic cascade propagation comparison only; no service fault injection or self-healing evidence."}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
