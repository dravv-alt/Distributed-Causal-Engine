"""Bounded archive of official, permissively licensed reference source only."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'docs/research-design/2026-10-08-bounded-acquisition/official-reference.json'
COMMIT = 'c1bd4af7f635171a1c31cdd567c07d698dff6abc'
FILES = ['README.md', 'LICENSE', 'rca/baseline/rca_agent/prompt/basic_prompt_Bank.py', 'rca/baseline/rca_agent/prompt/basic_prompt_Market.py', 'rca/baseline/rca_agent/prompt/basic_prompt_Telecom.py', 'rca/baseline/rca_agent/prompt/agent_prompt.py']


def main():
    if OUT.exists():
        raise FileExistsError('Refusing to overwrite dated official-reference archive')
    records=[]
    for path in FILES:
        url=f'https://raw.githubusercontent.com/microsoft/OpenRCA/{COMMIT}/{path}'
        with urlopen(Request(url,headers={'User-Agent':'DCE-bounded-read-only-reference'}),timeout=20) as r:
            raw=r.read(32769)
            if len(raw)>32768:
                raise ValueError('Reference file exceeds scope cap: '+path)
        records.append({'path':path,'url':url,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'text':raw.decode('utf-8')})
    license_text=next(r['text'] for r in records if r['path']=='LICENSE')
    if 'MIT License' not in license_text:
        raise ValueError('Expected permissive source license not established')
    with OUT.open('x',encoding='utf-8') as f:
        json.dump({'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'upstream_commit':COMMIT,'dataset_version_match':'UNKNOWN','source_author':'Microsoft/OpenRCA contributors; original license preserved','scope':'External documentation/code archive; examples and heuristics are not local findings','records':records},f,indent=2,ensure_ascii=False)
    print(json.dumps({'files':len(records),'bytes':sum(r['bytes'] for r in records),'archive':str(OUT.relative_to(ROOT))}))


if __name__=='__main__':
    main()
