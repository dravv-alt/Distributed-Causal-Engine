from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

BASE=Path(__file__).resolve().parents[1]
RUN=BASE/"results"/"E018-R001"


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def ranks(v):
    ids=sorted(v); order=sorted(ids,key=lambda n:(-v[n],n)); out={}; i=0
    while i<len(order):
        j=i+1
        while j<len(order) and v[order[j]]==v[order[i]]: j+=1
        s=1-(((i+1)+j)/2-1)/max(1,len(order)-1)
        for n in order[i:j]: out[n]=s
        i=j
    return out


def expected_disabled(case):
    ids=[n["service_id"] for n in case["nodes"]]; nodes={n["service_id"]:n for n in case["nodes"]}; adj={n:[] for n in ids}
    for a,b in case["edges"]: adj[a].append(b)
    reach={}
    for n in ids:
        seen=set(); todo=list(adj[n])
        while todo:
            x=todo.pop()
            if x in seen: continue
            seen.add(x); todo.extend(adj[x])
        reach[n]=seen
    modalities=[ranks({n:-nodes[n]["onset"] for n in ids}), ranks({n:nodes[n]["symbolic_score"] for n in ids}), ranks({n:float(len(reach[n])) for n in ids})]
    return {n:sum(m[n] for m in modalities)/3 for n in ids}, reach


def main():
    pfile=RUN/"predictions.json"; seal=json.loads((RUN/"prediction-seal.json").read_text())
    assert sha(pfile)==seal["prediction_sha256"] and seal["labels_loaded"] is False
    inputs=json.loads((BASE/"fixtures/test-inputs.json").read_text())["cases"]
    pred=json.loads(pfile.read_text())["predictions"]
    labels=json.loads((BASE/"fixtures/evaluator-only/test-labels.json").read_text())["case_labels"]
    report=json.loads((RUN/"evaluation.json").read_text())
    assert len(inputs)==len(pred)==600 and set(labels)=={r["scenario_id"] for r in pred}
    input_by={x["scenario_id"]:x for x in inputs}
    audit_counts={"neural_disabled_scores_recomputed_without_neural":0,"arm_metrics_recomputed":0,"calibration_diagnostics_recomputed":0}
    for method in ("full_fusion","neural_disabled"):
        hits=top3=abst=explained=pathok=false=0; rr=[]; bs=[]; conf=[]; correct=[]
        for row in pred:
            name=row["scenario_id"]; arm=row["arms"][method]; truth=labels[name]
            if method=="neural_disabled":
                expected,reach=expected_disabled(input_by[name])
                assert max(abs(expected[k]-arm["scores"][k]) for k in expected)<1e-12
                audit_counts["neural_disabled_scores_recomputed_without_neural"]+=1
                if arm["ranking"][0] in reach and reach[arm["ranking"][0]]:
                    assert arm["explanation_path"][1]==sorted(reach[arm["ranking"][0]])[0]
            rank=arm["ranking"].index(truth["root"])+1; hits+=rank==1; top3+=rank<=3; rr.append(1/rank)
            abst+=arm["abstained"]; false+=(rank!=1 and not arm["abstained"])
            path=arm["explanation_path"]; explained+=bool(path); pathok+=bool(path and path[0]==truth["root"] and path[1] in truth["affected_descendants"])
            ids=sorted(arm["scores"]); logits=np.array([arm["scores"][x]/.1 for x in ids]); probs=np.exp(logits-logits.max()); probs/=probs.sum()
            one=np.array([float(x==truth["root"]) for x in ids]); bs.append(float(np.sum((probs-one)**2)))
            k=int(probs.argmax()); conf.append(float(probs[k])); correct.append(float(ids[k]==truth["root"]))
        n=len(pred); cov=n-abst
        ece=0
        for lo in np.linspace(0,1,11)[:-1]:
            ix=[i for i,c in enumerate(conf) if c>=lo and c<(lo+.1 if lo<.9 else 1.0000001)]
            if ix: ece+=len(ix)/n*abs(np.mean([conf[i] for i in ix])-np.mean([correct[i] for i in ix]))
        metrics={"top1":hits/n,"top3":top3/n,"mrr":float(np.mean(rr)),"false_diagnosis_rate_nonabstained":false/cov,"abstention_rate":abst/n,"coverage":cov/n,"explanation_coverage":explained/n,"path_accuracy_among_cases":pathok/n,"path_accuracy_when_explained":pathok/explained,"calibration_diagnostic":{"multiclass_brier":float(np.mean(bs)),"top_label_ece_10bin":float(ece),"softmax_temperature":0.1}}
        for key,val in metrics.items():
            if isinstance(val,dict):
                for sub,sv in val.items(): assert abs(report["metrics"][method][key][sub]-sv)<1e-12
                audit_counts["calibration_diagnostics_recomputed"]+=1
            else: assert abs(report["metrics"][method][key]-val)<1e-12
        audit_counts["arm_metrics_recomputed"]+=1
    audit={"audit":"E018-R001 independent modality-ablation recomputation","passed":True,"cases":600,"checks":["prediction seal and label separation","600/600 neural-disabled score vectors recomputed from topology, temporal, and symbolic inputs only","neural-disabled explanation endpoint does not use neural feature","both arms localization, abstention, explanation, path and calibration diagnostics independently recomputed"],"counts":audit_counts,"hashes":{"predictions":sha(pfile),"inputs":sha(BASE/"fixtures/test-inputs.json"),"labels":sha(BASE/"fixtures/evaluator-only/test-labels.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n")
    print(json.dumps(audit,indent=2))


if __name__=="__main__":main()
