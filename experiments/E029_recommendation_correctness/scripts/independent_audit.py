from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E029-R001";MAP={"cpu_saturation":"scale_service","database_saturation":"repair_database","network_path_bottleneck":"reroute_traffic"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pf=RUN/"recommendations.json";seal=json.loads((RUN/"prediction-seal.json").read_text());assert sha(pf)==seal["recommendations_sha256"] and not seal["evaluator_labels_loaded"] and not seal["actions_executed"]
    rows=json.loads(pf.read_text())["recommendations"];inputs=json.loads((BASE/"fixtures/inputs.json").read_text())["cases"];oracle=json.loads((BASE/"fixtures/evaluator-only/mechanisms-and-oracle.json").read_text())["cases"];report=json.loads((RUN/"evaluation.json").read_text());by={c["scenario_id"]:c for c in inputs}
    correct=consistent=unknown=abstain=unknown_recommend=wrong=0
    for r in rows:
        d=by[r["scenario_id"]]["diagnosed_mechanism"];truth=oracle[r["scenario_id"]]
        expected=MAP.get(d);assert r["recommendation"]==expected and r["abstained"]==(expected is None)
        if expected is not None:consistent+=r["recommendation"]==MAP[d];correct+=r["recommendation"]==truth["oracle_action"]
        else:unknown+=1;abstain+=r["abstained"];unknown_recommend+=r["recommendation"] is not None
        wrong+=truth["diagnosis_class"]=="incorrect"
    assert consistent==report["diagnosis_to_action_consistency"]["correct_mapping"] and correct==report["recommendation_correctness_vs_true_mechanism"]["correct"] and unknown==report["unknown_diagnosis"]["n"] and abstain==report["unknown_diagnosis"]["abstained"] and unknown_recommend==report["unknown_diagnosis"]["false_recommendations"] and wrong==report["wrong_diagnosis_cases"]
    audit={"audit":"E029-R001 independent recommendation audit","passed":True,"cases":len(rows),"checks":["sealed labels-free inference","mapping consistency recomputed","recommendation correctness versus hidden mechanism recomputed","unknown abstention and diagnosis-error counts recomputed","zero action execution"],"hashes":{"recommendations":sha(pf),"inputs":sha(BASE/"fixtures/inputs.json"),"oracle":sha(BASE/"fixtures/evaluator-only/mechanisms-and-oracle.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
