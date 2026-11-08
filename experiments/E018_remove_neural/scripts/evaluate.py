from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

BASE=Path(__file__).resolve().parents[1]
RUN=BASE/"results"/"E018-R001"
ARMS=("full_fusion","neural_disabled")


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def wilson(x,n):
    z=1.959963984540054; p=x/n; d=1+z*z/n
    c=(p+z*z/(2*n))/d; h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [float(c-h),float(c+h)]


def calibration(rows,labels,arm):
    brier=[]; conf=[]; correct=[]
    for row in rows:
        scores=row["arms"][arm]["scores"]
        ids=sorted(scores)
        logits=np.asarray([scores[x]/0.1 for x in ids],dtype=float)
        probs=np.exp(logits-logits.max()); probs/=probs.sum()
        target=labels[row["scenario_id"]]["root"]
        onehot=np.asarray([1.0 if x==target else 0.0 for x in ids])
        brier.append(float(np.sum((probs-onehot)**2)))
        k=int(np.argmax(probs)); conf.append(float(probs[k])); correct.append(float(ids[k]==target))
    ece=0.0
    for lo in np.linspace(0,1,11)[:-1]:
        ix=[i for i,c in enumerate(conf) if (c>=lo and c<(lo+0.1 if lo<0.9 else 1.0000001))]
        if ix: ece += len(ix)/len(conf)*abs(float(np.mean([conf[i] for i in ix]))-float(np.mean([correct[i] for i in ix])))
    return {"multiclass_brier":float(np.mean(brier)),"top_label_ece_10bin":float(ece),"softmax_temperature":0.1}


def get_metrics(rows,labels,arm):
    ranks=[]; top3=abstain=false=explained=pathok=0
    for r in rows:
        m=r["arms"][arm]; truth=labels[r["scenario_id"]]
        rank=m["ranking"].index(truth["root"])+1; ranks.append(rank)
        top3 += rank<=3; abstain += m["abstained"]
        false += (rank!=1 and not m["abstained"])
        path=m["explanation_path"]; explained += bool(path)
        pathok += bool(path and path[0]==truth["root"] and path[1] in truth["affected_descendants"])
    n=len(rows); hit=sum(x==1 for x in ranks); coverage=n-abstain
    return {"n":n,"top1":hit/n,"top1_wilson95":wilson(hit,n),"top3":top3/n,"mrr":float(np.mean([1/x for x in ranks])),"false_diagnosis_rate_nonabstained":false/coverage if coverage else None,"abstention_rate":abstain/n,"coverage":coverage/n,"explanation_coverage":explained/n,"path_accuracy_among_cases":pathok/n,"path_accuracy_when_explained":pathok/explained if explained else None,"calibration_diagnostic":calibration(rows,labels,arm)}


def main():
    predpath=RUN/"predictions.json"; seal=json.loads((RUN/"prediction-seal.json").read_text())
    if seal["prediction_sha256"]!=sha(predpath) or seal["labels_loaded"] is not False: raise SystemExit("prediction seal invalid")
    rows=json.loads(predpath.read_text())["predictions"]
    labelpath=BASE/"fixtures"/"evaluator-only"/"test-labels.json"
    labels=json.loads(labelpath.read_text())["case_labels"]
    if set(labels)!={r["scenario_id"] for r in rows}: raise SystemExit("labels/predictions mismatch")
    metrics={arm:get_metrics(rows,labels,arm) for arm in ARMS}
    base=np.asarray([r["arms"]["full_fusion"]["ranking"][0]==labels[r["scenario_id"]]["root"] for r in rows],dtype=np.int8)
    disabled=np.asarray([r["arms"]["neural_disabled"]["ranking"][0]==labels[r["scenario_id"]]["root"] for r in rows],dtype=np.int8)
    rng=np.random.default_rng(18015); ix=rng.integers(0,len(rows),size=(10000,len(rows)))
    dtop=(disabled[ix].mean(1)-base[ix].mean(1)).tolist()
    mrr_full=np.asarray([1/(r["arms"]["full_fusion"]["ranking"].index(labels[r["scenario_id"]]["root"])+1) for r in rows])
    mrr_disabled=np.asarray([1/(r["arms"]["neural_disabled"]["ranking"].index(labels[r["scenario_id"]]["root"])+1) for r in rows])
    dmrr=(mrr_disabled[ix].mean(1)-mrr_full[ix].mean(1)).tolist()
    result={"experiment":"E018-R001","planning_stage":"XP015","dataset":"synthetic held-out cases, fresh generator seed","metrics":metrics,"paired_neural_disabled_minus_full":{"top1_difference":float(disabled.mean()-base.mean()),"top1_bootstrap95":[float(np.quantile(dtop,.025)),float(np.quantile(dtop,.975))],"mrr_difference":float(mrr_disabled.mean()-mrr_full.mean()),"mrr_bootstrap95":[float(np.quantile(dmrr,.025)),float(np.quantile(dmrr,.975))],"replicates":10000,"seed":18015},"provenance":{"prediction_sha256":sha(predpath),"input_sha256":sha(BASE/"fixtures"/"test-inputs.json"),"label_sha256":sha(labelpath)},"interpretation":"Synthetic ablation only. Softmax rank scores are calibration diagnostics, not calibrated DCE probabilities."}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__": main()
