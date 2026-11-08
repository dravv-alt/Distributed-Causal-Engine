from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np

BASE = Path(__file__).resolve().parents[1]
INPUT = BASE / "fixtures" / "test-inputs.json"
RUN = BASE / "results" / "E018-R001"


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def rank_scores(values):
    names = sorted(values)
    ordered = sorted(names, key=lambda name: (-values[name], name))
    out = {}; i = 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and values[ordered[j]] == values[ordered[i]]: j += 1
        score = 1 - (((i + 1) + j) / 2 - 1) / max(1, len(ordered) - 1)
        for name in ordered[i:j]: out[name] = float(score)
        i = j
    return out


def predict(case):
    ids = [n["service_id"] for n in case["nodes"]]
    by = {n["service_id"]: n for n in case["nodes"]}
    adj = {name: [] for name in ids}
    for a,b in case["edges"]: adj[a].append(b)
    reaches = {}
    for name in ids:
        seen=set(); todo=list(adj[name])
        while todo:
            nxt=todo.pop()
            if nxt in seen: continue
            seen.add(nxt); todo.extend(adj[nxt])
        reaches[name]=seen
    mods = {
        "neural": rank_scores({n: by[n]["neural_signal"] for n in ids}),
        "symbolic": rank_scores({n: by[n]["symbolic_score"] for n in ids}),
        "temporal": rank_scores({n: -by[n]["onset"] for n in ids}),
        "topology": rank_scores({n: float(len(reaches[n])) for n in ids}),
    }
    methods={}
    for name, use in (("full_fusion", ("neural","topology","temporal","symbolic")), ("neural_disabled", ("topology","temporal","symbolic"))):
        scores={service: float(sum(mods[m][service] for m in use)/len(use)) for service in ids}
        ranking=sorted(ids,key=lambda x:(-scores[x],x))
        path=[]
        if reaches[ranking[0]]:
            endpoint=(max(reaches[ranking[0]],key=lambda x:(by[x]["neural_signal"],x)) if name=="full_fusion" else sorted(reaches[ranking[0]])[0])
            path=[ranking[0],endpoint]
        methods[name]={"ranking":ranking,"scores":scores,"abstained":scores[ranking[0]]-scores[ranking[1]]<.05,"explanation_path":path}
    return {"scenario_id":case["scenario_id"],"arms":methods}


def main():
    cases=json.loads(INPUT.read_text(encoding="utf-8"))["cases"]
    rows=[predict(case) for case in cases]
    RUN.mkdir(parents=True,exist_ok=True)
    out=RUN/"predictions.json"
    out.write_text(json.dumps({"predictions":rows},indent=2)+"\n",encoding="utf-8")
    seal={"prediction_sha256":sha(out),"input_sha256":sha(INPUT),"labels_loaded":False,"network_used":False,"device":"cpu","python":sys.version,"platform":platform.platform(),"numpy":np.__version__}
    (RUN/"prediction-seal.json").write_text(json.dumps(seal,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"predictions":len(rows),"arms":["full_fusion","neural_disabled"],"neural_feature_used_in_disabled_arm":False,"labels_loaded":False,"sealed":True},indent=2))


if __name__=="__main__": main()
