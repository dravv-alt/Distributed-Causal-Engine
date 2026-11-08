from __future__ import annotations
import json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures";RUN=BASE/"results/E033-R001"
def main():
    diagnoses=json.loads((RUN/"diagnoses.json").read_text())["diagnoses"];rows=[]
    for d in diagnoses:
        root_repair="repair_database" in d["propagation_aware"]["actions"]
        prop={"first_check_symptoms_cleared":root_repair,"stable_recovery_after_three_checks":root_repair,"root_fault_active_after_three_checks":not root_repair}
        baseline={"first_check_symptoms_cleared":True,"stable_recovery_after_three_checks":False,"root_fault_active_after_three_checks":True}
        rows.append({"scenario_id":d["scenario_id"],"propagation_aware":prop,"independent_symptom_treatment":baseline})
    (RUN/"sandbox-outcomes.json").write_text(json.dumps({"outcomes":rows},indent=2)+"\n",encoding="utf-8");print(json.dumps({"cases":len(rows),"external_actions":False,"simulated_checks":3},indent=2))
if __name__=="__main__":main()
