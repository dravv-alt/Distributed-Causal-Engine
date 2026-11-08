import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CLASSES=["connection_pool_exhaustion","timeout","healthy"]
WORDS={"connection_pool_exhaustion":["connection pool exhausted","pool has no available connection","database pool limit reached","connection checkout failed"],"timeout":["request timed out","upstream deadline exceeded","operation exceeded timeout","service response took too long"],"healthy":["request completed successfully","health check passed","operation completed normally","service is ready"]}
train=[]; train_y=[]; tests=[]; test_y=[]
for ci,name in enumerate(CLASSES):
    for i in range(100):
        train.append({"text":f"{WORDS[name][i%4]}; worker={i%7}; attempt={i%3}","service":f"service-{i%4}","timestamp":1700000000+i,"source_id":f"SYN-TR-{ci}-{i:03d}"}); train_y.append(ci)
    for i in range(50):
        tests.append({"text":f"{WORDS[name][(i+1)%4]}; worker={i%5}; attempt={i%4}","service":f"service-{i%4}","timestamp":1700100000+i,"source_id":f"SYN-TE-{ci}-{i:03d}"}); test_y.append(ci)
(ROOT/"fixtures"/"train.json").write_text(json.dumps(train,indent=2)+"\n")
(ROOT/"fixtures"/"test_inputs.json").write_text(json.dumps(tests,indent=2)+"\n")
(ROOT/"evaluator"/"train_labels.json").write_text(json.dumps(train_y)+"\n")
(ROOT/"evaluator"/"test_labels.json").write_text(json.dumps(test_y)+"\n")
