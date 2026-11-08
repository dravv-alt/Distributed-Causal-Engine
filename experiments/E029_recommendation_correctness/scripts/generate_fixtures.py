from __future__ import annotations
import json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures";MECH=("cpu_saturation","database_saturation","network_path_bottleneck");ACTION={"cpu_saturation":"scale_service","database_saturation":"repair_database","network_path_bottleneck":"reroute_traffic"}
def main():
    rng=np.random.default_rng(29026);cases=[];labels={};i=0
    for true in MECH:
        wrong=[m for m in MECH if m!=true]
        diagnoses=[true]*140+[str(rng.choice(wrong)) for _ in range(40)]+["UNKNOWN"]*20;rng.shuffle(diagnoses)
        for diag in diagnoses:
            sid=f"REC-{i:04d}";cases.append({"scenario_id":sid,"diagnosed_mechanism":diag});labels[sid]={"true_mechanism":true,"oracle_action":ACTION[true],"diagnosis_class":"unknown" if diag=="UNKNOWN" else "correct" if diag==true else "incorrect"};i+=1
    rng.shuffle(cases)
    (FIX/"evaluator-only").mkdir(parents=True,exist_ok=True)
    (FIX/"inputs.json").write_text(json.dumps({"version":"synthetic-recommendation-cases-v1","cases":cases},indent=2)+"\n",encoding="utf-8")
    (FIX/"evaluator-only"/"mechanisms-and-oracle.json").write_text(json.dumps({"cases":labels},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(cases),"correct_diagnosis":420,"wrong_diagnosis":120,"unknown":60,"labels_separated":True},indent=2))
if __name__=="__main__":main()
