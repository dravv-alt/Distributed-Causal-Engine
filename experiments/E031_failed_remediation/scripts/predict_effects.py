from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];INPUT=BASE/"fixtures/inputs.json";RUN=BASE/"results/E031-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def expected(c):
    s=c["initial_state"].copy();a=c["action"]
    if a=="restart":s["generation"]+=1;s["last_action"]="restart"
    elif a=="scale":s["replicas"]+=1;s["healthy_replicas"]+=1;s["last_action"]="scale"
    elif a=="reroute":s["route"]=c["arguments"]["target"];s["last_action"]="reroute"
    return s
def main():
    cases=json.loads(INPUT.read_text())["cases"];rows=[{"scenario_id":c["scenario_id"],"action":c["action"],"expected_state":expected(c)} for c in cases]
    RUN.mkdir(parents=True,exist_ok=True);p=RUN/"predictions.json";p.write_text(json.dumps({"predictions":rows},indent=2)+"\n",encoding="utf-8")
    (RUN/"prediction-seal.json").write_text(json.dumps({"predictions_sha256":sha(p),"input_sha256":sha(INPUT),"failure_schedule_loaded":False,"failure_labels_loaded":False},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"predictions":len(rows),"failure_schedule_loaded":False,"sealed":True},indent=2))
if __name__=="__main__":main()
