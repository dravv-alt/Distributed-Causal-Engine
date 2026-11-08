import json, re, platform
from pathlib import Path
import torch
from torch import nn

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "E036-R001"
CLASSES = ["connection_pool_exhaustion", "timeout", "healthy"]
WORDS = {
 "connection_pool_exhaustion": ["connection pool exhausted", "pool has no available connection", "database pool limit reached", "connection checkout failed"],
 "timeout": ["request timed out", "upstream deadline exceeded", "operation exceeded timeout", "service response took too long"],
 "healthy": ["request completed successfully", "health check passed", "operation completed normally", "service is ready"],
}
def vec(text, vocab):
    counts = {}
    for token in re.findall(r"[a-z]+", text.lower()): counts[token] = counts.get(token, 0) + 1
    return [float(counts.get(w, 0)) for w in vocab]
def f1_macro(truth, pred):
    vals=[]
    for c in range(len(CLASSES)):
        tp=sum(a==c and b==c for a,b in zip(truth,pred)); fp=sum(a!=c and b==c for a,b in zip(truth,pred)); fn=sum(a==c and b!=c for a,b in zip(truth,pred))
        vals.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)
    return sum(vals)/len(vals)
def main():
    torch.manual_seed(36033); torch.set_num_threads(1)
    train=json.loads((ROOT/"fixtures"/"train.json").read_text())
    tests=json.loads((ROOT/"fixtures"/"test_inputs.json").read_text())
    train_labels=json.loads((ROOT/"evaluator"/"train_labels.json").read_text())
    vocab=sorted({w for row in train for w in re.findall(r"[a-z]+", row["text"].lower())})
    x=torch.tensor([vec(r["text"],vocab) for r in train],dtype=torch.float32); y=torch.tensor(train_labels,dtype=torch.long)
    model=nn.Linear(len(vocab),len(CLASSES)); opt=torch.optim.Adam(model.parameters(),lr=0.04)
    for _ in range(180):
        opt.zero_grad(); loss=nn.functional.cross_entropy(model(x),y); loss.backward(); opt.step()
    tx=torch.tensor([vec(r["text"],vocab) for r in tests],dtype=torch.float32)
    with torch.no_grad(): probs=torch.softmax(model(tx),dim=1); pred=probs.argmax(1).tolist()
    outputs=[]
    for row, cls, p in zip(tests,pred,probs.tolist()):
        outputs.append({"event_type":CLASSES[cls],"service":row["service"],"timestamp":row["timestamp"],"source_id":row["source_id"],"confidence":max(p)})
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"predictions.json").write_text(json.dumps(outputs,indent=2)+"\n")
    (OUT/"runtime.json").write_text(json.dumps({"python":platform.python_version(),"torch":torch.__version__,"device":"CPU","epochs":180,"vocabulary_size":len(vocab)},indent=2)+"\n")
    print(json.dumps({"train":len(train),"test":len(tests),"vocab":len(vocab),"test_labels_loaded":False}))
if __name__=="__main__": main()
