from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E024-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pf=RUN/"predictions.json";seal=json.loads((RUN/"prediction-seal.json").read_text())
    if seal["prediction_sha256"]!=sha(pf) or seal["labels_loaded"] is not False or seal["intervention_outcomes_loaded"] is not False:raise SystemExit("seal invalid")
    pred=json.loads(pf.read_text())["predictions"];lp=BASE/"fixtures/evaluator-only/intervention-outcomes.json";oracle=json.loads(lp.read_text())["outcomes"]
    if set(oracle)!={r["context_id"] for r in pred}:raise SystemExit("oracle alignment mismatch")
    model_abs=[];base_abs=[];model_sq=[];base_sq=[];sign=[];path=[];changes=[]
    for r in pred:
        y0=r["observed_y_do_0"];y1=oracle[r["context_id"]]["y_do_1"];p=r["predicted_y_do_1"];effect=p-y0;actual=y1-y0
        model_abs.append(abs(p-y1));base_abs.append(abs(y0-y1));model_sq.append((p-y1)**2);base_sq.append((y0-y1)**2);sign.append((effect>=0)==(actual>=0));path.append(effect>=.5);changes.append(abs(p-y1)-abs(y0-y1))
    rng=np.random.default_rng(24022);ix=rng.integers(0,len(pred),size=(10000,len(pred)));delta=np.asarray(changes)[ix].mean(1)
    result={"experiment":"E024-R001","planning_stage":"XP021","n_contexts":len(pred),"counterfactual_prediction":{"mae":float(np.mean(model_abs)),"rmse":float(np.sqrt(np.mean(model_sq))),"effect_direction_consistency":float(np.mean(sign)),"positive_path_accuracy_against_known_effect":float(np.mean(path))},"no_change_baseline":{"mae":float(np.mean(base_abs)),"rmse":float(np.sqrt(np.mean(base_sq))),"positive_path_accuracy":0.0},"paired_model_minus_no_change_absolute_error":{"difference":float(np.mean(changes)),"bootstrap95":[float(np.quantile(delta,.025)),float(np.quantile(delta,.975))],"replicates":10000,"seed":24022},"provenance":{"prediction_sha256":sha(pf),"input_sha256":sha(BASE/"fixtures/heldout-inputs.json"),"training_sha256":sha(BASE/"fixtures/training.json"),"intervention_oracle_sha256":sha(lp)},"assumptions":["invariant linear equation","measured U is sufficient","no interference","same noise law","synthetic matched potential outcomes"],"interpretation":"Known synthetic counterfactual validation only; not a real service intervention prediction."}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
