from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E033-R001";FIX=BASE/"fixtures"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    dp=RUN/"diagnoses.json";seal=json.loads((RUN/"prediction-seal.json").read_text());assert sha(dp)==seal["diagnoses_sha256"] and not seal["root_labels_loaded"]
    cases=json.loads((FIX/"inputs.json").read_text())["cases"];ds=json.loads(dp.read_text())["diagnoses"];out=json.loads((RUN/"sandbox-outcomes.json").read_text())["outcomes"];labels=json.loads((FIX/"evaluator-only/root-labels.json").read_text())["labels"];report=json.loads((RUN/"evaluation.json").read_text());ob={x["scenario_id"]:x for x in out};right=pathright=stable=baselinestable=0
    for c,d in zip(cases,ds):
        graph={n:[] for n in c["symptoms"]}
        for a,b in c["causal_edges"]:graph[a].append(b)
        counts={}
        for node in graph:
            seen=set();todo=list(graph[node])
            while todo:
                x=todo.pop()
                if x in seen:continue
                seen.add(x);todo.extend(graph[x])
            counts[node]=len(seen)
        root=max((x for x,v in c["symptoms"].items() if v),key=lambda x:(counts[x],-c["onset"][x],x));path=[root];cur=root
        while graph[cur]:cur=graph[cur][0];path.append(cur)
        assert d["propagation_aware"]["root"]==root and d["propagation_aware"]["path"]==path
        right+=root==labels[c["scenario_id"]]["root"];pathright+=path==labels[c["scenario_id"]]["propagation_path"]
        expected_stable="repair_database" in d["propagation_aware"]["actions"];assert ob[c["scenario_id"]]["propagation_aware"]["stable_recovery_after_three_checks"]==expected_stable;stable+=expected_stable
        assert not ob[c["scenario_id"]]["independent_symptom_treatment"]["stable_recovery_after_three_checks"];baselinestable+=0
    assert right/len(cases)==report["propagation_aware"]["root_accuracy"] and pathright/len(cases)==report["propagation_aware"]["path_accuracy"] and stable/len(cases)==report["propagation_aware"]["stable_recovery_at_three_checks"] and baselinestable/len(cases)==report["independent_symptom_treatment"]["stable_recovery_at_three_checks"]
    audit={"audit":"E033-R001 independent cascade graph audit","passed":True,"cases":len(cases),"checks":["label-blind prediction seal","root and path independently recomputed from causal graph","stable root-repair effect recomputed","symptom-only recurrence retained"],"hashes":{"diagnoses":sha(dp),"outcomes":sha(RUN/"sandbox-outcomes.json"),"labels":sha(FIX/"evaluator-only/root-labels.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
