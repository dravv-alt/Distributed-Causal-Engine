from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/"experiments/E020_remove_temporal";SRC=ROOT/"experiments/E017_fusion_ablation/scripts/generate_fixtures.py"
sp=importlib.util.spec_from_file_location("frozen_generator",SRC);gen=importlib.util.module_from_spec(sp);sp.loader.exec_module(gen)
def main():
    rng=np.random.default_rng(30017);cases=[];labels={}
    for i in range(600):
        c,y=gen.make_case(i,rng);cases.append(c);labels[c["scenario_id"]]=y
    d=BASE/"fixtures";(d/"evaluator-only").mkdir(parents=True,exist_ok=True)
    (d/"test-inputs.json").write_text(json.dumps({"version":"synthetic-fusion-v1-seed-30017","cases":cases},indent=2)+"\n",encoding="utf-8")
    (d/"evaluator-only/test-labels.json").write_text(json.dumps({"case_labels":labels},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(cases),"labels_separated":True,"seed":30017},indent=2))
if __name__=="__main__":main()
