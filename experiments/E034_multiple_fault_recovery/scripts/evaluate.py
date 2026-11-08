from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E034-R001";FIX=BASE/"fixtures"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    dp=RUN/"diagnoses.json";seal=json.loads((RUN/"prediction-seal.json").read_text())
    if seal["diagnoses_sha256"]!=sha(dp) or seal["root_schedule_loaded"] is not False:raise SystemExit("seal invalid")
    diagnoses=json.loads(dp.read_text())["diagnoses"];out=json.loads((RUN/"sandbox-outcomes.json").read_text())["outcomes"];labels=json.loads((FIX/"evaluator-only/root-labels.json").read_text())["roots"];ob={x["scenario_id"]:x for x in out};exact=multi_recovered=single_recovered=joint=joint_multi=joint_single=interference=0
    for d in diagnoses:
        y=set(labels[d["scenario_id"]]["root_set"]);exact+=set(d["multi_root"]["roots"])==y;m=ob[d["scenario_id"]];multi_recovered+=not any(m["multi_root_final"].values());single_recovered+=not any(m["single_root_final"].values());interference+=m["order_interference"]
        if len(y)>1:joint+=1;joint_multi+=not any(m["multi_root_final"].values());joint_single+=not any(m["single_root_final"].values())
    n=len(diagnoses)
    result={"experiment":"E034-R001","planning_stage":"XP031","cases":n,"multi_root_exact_set_accuracy":exact/n,"multi_root_recovery_rate":multi_recovered/n,"single_root_baseline_recovery_rate":single_recovered/n,"joint_fault_cases":joint,"joint_multi_root_recovery":joint_multi/joint,"joint_single_root_baseline_recovery":joint_single/joint,"action_order_interference_cases":interference,"provenance":{"diagnoses_sha256":sha(dp),"outcomes_sha256":sha(RUN/"sandbox-outcomes.json"),"input_sha256":sha(FIX/"inputs.json"),"root_label_sha256":sha(FIX/"evaluator-only/root-labels.json")},"interpretation":"Synthetic simultaneous-fault and action-commutativity simulation only."}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
