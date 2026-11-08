from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];TRAIN=BASE/"fixtures/training.json";OUT=BASE/"results/E024-R001/model.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    obs=json.loads(TRAIN.read_text())["observations"];a=np.array([x["a"] for x in obs]);u=np.array([x["u"] for x in obs]);y=np.array([x["y"] for x in obs])
    coeff=np.linalg.lstsq(np.column_stack([np.ones(len(a)),a,u]),y,rcond=None)[0].tolist()
    OUT.parent.mkdir(parents=True,exist_ok=True);record={"model":"OLS: y ~ intercept + a + u","coefficients":coeff,"training_rows":len(obs),"training_sha256":sha(TRAIN)}
    OUT.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8");print(json.dumps(record,indent=2))
if __name__=="__main__":main()
