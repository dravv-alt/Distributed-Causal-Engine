from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E029-R001";MAP={"cpu_saturation":"scale_service","database_saturation":"repair_database","network_path_bottleneck":"reroute_traffic"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pf=RUN/"recommendations.json";seal=json.loads((RUN/"prediction-seal.json").read_text())
    if seal["recommendations_sha256"]!=sha(pf) or seal["evaluator_labels_loaded"] is not False:raise SystemExit("seal invalid")
    rows=json.loads(pf.read_text())["recommendations"];truth=json.loads((BASE/"fixtures/evaluator-only/mechanisms-and-oracle.json").read_text())["cases"]
    if {r["scenario_id"] for r in rows}!=set(truth):raise SystemExit("coverage mismatch")
    covered=[r for r in rows if not r["abstained"]]
    inputs={c["scenario_id"]:c for c in json.loads((BASE/"fixtures/inputs.json").read_text())["cases"]}
    consistent=sum(r["recommendation"]==MAP[inputs[r["scenario_id"]]["diagnosed_mechanism"]] for r in covered)
    correct=sum(r["recommendation"]==truth[r["scenario_id"]]["oracle_action"] for r in covered)
    unknown=[r for r in rows if inputs[r["scenario_id"]]["diagnosed_mechanism"]=="UNKNOWN"]
    result={"experiment":"E029-R001","planning_stage":"XP026","cases":len(rows),"covered_recommendations":len(covered),"diagnosis_to_action_consistency":{"correct_mapping":consistent,"n":len(covered)},"recommendation_correctness_vs_true_mechanism":{"correct":correct,"n":len(covered),"accuracy":correct/len(covered) if covered else None},"unknown_diagnosis":{"n":len(unknown),"abstained":sum(r["abstained"] for r in unknown),"false_recommendations":sum(r["recommendation"] is not None for r in unknown)},"wrong_diagnosis_cases":sum(truth[r["scenario_id"]]["diagnosis_class"]=="incorrect" for r in rows),"actions_executed":False,"provenance":{"recommendations_sha256":sha(pf),"input_sha256":sha(BASE/"fixtures/inputs.json"),"oracle_sha256":sha(BASE/"fixtures/evaluator-only/mechanisms-and-oracle.json")},"interpretation":"Synthetic mapping and diagnosis-error visibility only."}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
