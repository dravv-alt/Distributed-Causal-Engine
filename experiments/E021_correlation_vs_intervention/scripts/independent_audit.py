from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E021-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pf=RUN/"predictions.json";seal=json.loads((RUN/"prediction-seal.json").read_text());assert sha(pf)==seal["prediction_sha256"] and seal["labels_loaded"] is False
    cases=json.loads((BASE/"fixtures/inputs.json").read_text())["cases"];rows=json.loads(pf.read_text())["predictions"];labels=json.loads((BASE/"fixtures/evaluator-only/mechanism-labels.json").read_text())["mechanisms"];published=json.loads((RUN/"evaluation.json").read_text());by={c["scenario_id"]:c for c in cases}
    for r in rows:
        c=by[r["scenario_id"]];a=np.array([q["a"] for q in c["observations"]]);y=np.array([q["y"] for q in c["observations"]]);corr=float(np.corrcoef(a,y)[0,1]);effect=float(np.mean([q["y_do_1"]-q["y_do_0"] for q in c["matched_interventions"]]))
        assert abs(corr-r["observational_correlation"])<1e-12 and abs(effect-r["intervention_effect_estimate"])<1e-12
        assert r["predictions"]["observational_rule"]==(abs(corr)>=.5) and r["predictions"]["intervention_rule"]==(effect>=.5)
    recomputed={}
    for arm in ("observational_rule","intervention_rule"):
        tp=fp=tn=fn=0
        for r in rows:
            actual=labels[r["scenario_id"]]=="direct_cause";p=r["predictions"][arm]
            if p and actual:tp+=1
            elif p and not actual:fp+=1
            elif not p and not actual:tn+=1
            else:fn+=1
        se=tp/(tp+fn);sp=tn/(tn+fp);recomputed[arm]={"true_positive":tp,"false_positive":fp,"true_negative":tn,"false_negative":fn,"sensitivity":se,"specificity":sp,"balanced_accuracy":(se+sp)/2,"false_causal_rate_common_cause":fp/(fp+tn),"causal_detection_rate_direct_cause":tp/(tp+fn)}
        for k,v in recomputed[arm].items():assert abs(v-published["metrics"][arm][k])<1e-12
    audit={"audit":"E021-R001 independent mechanism-label recomputation","passed":True,"cases":len(rows),"checks":["prediction seal and label separation","600/600 observational and intervention estimates independently recomputed","both decision rules recomputed from frozen thresholds","confusion matrices and causal false-positive rates recomputed"],"hashes":{"predictions":sha(pf),"inputs":sha(BASE/"fixtures/inputs.json"),"labels":sha(BASE/"fixtures/evaluator-only/mechanism-labels.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
