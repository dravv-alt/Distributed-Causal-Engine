from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];INPUT=BASE/"fixtures/inputs.json";RUN=BASE/"results/E029-R001"
ACTION={"cpu_saturation":"scale_service","database_saturation":"repair_database","network_path_bottleneck":"reroute_traffic"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rows=[]
    for c in json.loads(INPUT.read_text())["cases"]:
        d=c["diagnosed_mechanism"];rows.append({"scenario_id":c["scenario_id"],"recommendation":ACTION.get(d),"abstained":d not in ACTION})
    RUN.mkdir(parents=True,exist_ok=True);p=RUN/"recommendations.json";p.write_text(json.dumps({"recommendations":rows},indent=2)+"\n",encoding="utf-8")
    (RUN/"prediction-seal.json").write_text(json.dumps({"recommendations_sha256":sha(p),"input_sha256":sha(INPUT),"evaluator_labels_loaded":False,"actions_executed":False},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"recommendations":len(rows),"abstentions":sum(x["abstained"] for x in rows),"actions_executed":0,"sealed":True},indent=2))
if __name__=="__main__":main()
