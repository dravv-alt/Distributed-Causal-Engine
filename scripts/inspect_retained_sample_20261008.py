"""Bounded descriptive acquisition, not a symptom detector or experiment."""
import hashlib
import json
import sqlite3
import time
import zlib
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V006'
OUT=ROOT/'docs/research-design/2026-10-08-bounded-acquisition'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def bounded_inflate(payload):
    if len(payload)>2*1024*1024:
        raise ValueError('Compressed block cap exceeded')
    d=zlib.decompressobj()
    raw=d.decompress(payload,8*1024*1024+1)
    if len(raw)>8*1024*1024 or d.unconsumed_tail or not d.eof or d.unused_data:
        raise ValueError('Decompressed block cap or stream validation failed')
    rows=json.loads(raw)
    if not isinstance(rows,list) or len(rows)>1024:
        raise ValueError('Decoded block row cap exceeded')
    return rows


def choose(profiles):
    selected=[]
    for scenario in sorted({p['scenario'] for p in profiles}):
        eligible=sorted([p for p in profiles if p['scenario']==scenario and '/metric/' in p['path']],key=lambda p:p['path'])
        day=eligible[0]['path'].split('/telemetry/')[1].split('/')[0]
        for p in [p for p in eligible if '/telemetry/'+day+'/' in p['path']][:2]:
            selected.append({'scenario':scenario,'source_key':p['source_key'],'source_path':p['path'],'metric_names':sorted(p['metric_counts'])[:3],'timestamp_scale_inherited':p['selected_scale']})
    if len(selected)>8 or any(s['scenario'] not in s['source_path'] for s in selected):
        raise ValueError('Scenario-selection/cap violation')
    return selected


def main():
    plan_path=OUT/'sample-plan.json'
    result_path=OUT/'retained-sample-summary.json'
    if plan_path.exists() or result_path.exists():
        raise FileExistsError('Dated sample outputs exist; refusing overwrite')
    paths=sorted((BASE/'profiles').glob('*.json'))
    profile_hashes={str(p.relative_to(ROOT)).replace('\\','/'):sha(p.read_bytes()) for p in paths}
    profiles=[json.loads(p.read_text(encoding='utf-8')) for p in paths]
    selected=choose(profiles)
    reference_path=BASE/'context-reference.json'
    reference=json.loads(reference_path.read_text(encoding='utf-8'))
    dbpath=Path(reference['path']).resolve()
    if not dbpath.is_relative_to(ROOT/'experiments') or not dbpath.is_file():
        raise ValueError('Retained DB outside experiment boundary or absent')
    plan={'scope_record':str((OUT/'acquisition-scope.md').relative_to(ROOT)),'selected_sources':selected,'selection':'Earliest lexicographic date, first two metric paths, first three names; no values/labels inspected','limits':{'blocks':8,'rows_inspected_per_block':256,'rows_decoded_per_block':1024,'compressed_bytes_per_block':2097152,'decompressed_bytes_per_block':8388608,'sqlite_deadline_seconds':20},'profile_hashes':profile_hashes,'context_reference_sha256':sha(reference_path.read_bytes()),'database':str(dbpath.relative_to(ROOT)),'database_historical_sha256_not_reverified':reference['sha256']}
    # Exclusive plan creation precedes opening the DB or reading its payloads.
    with plan_path.open('x',encoding='utf-8') as f:json.dump(plan,f,indent=2)
    before=dbpath.stat()
    db=sqlite3.connect(dbpath.as_uri()+'?mode=ro&immutable=1',uri=True,timeout=2)
    db.execute('PRAGMA query_only=ON')
    deadline=time.monotonic()+20
    db.set_progress_handler(lambda: int(time.monotonic()>deadline),1000)
    reports=[]
    samples=[]
    try:
        for s in selected:
            catalog=db.execute('SELECT environment,path,status,report FROM sources WHERE source_key=?',(s['source_key'],)).fetchone()
            if not catalog or catalog[:3]!=(s['scenario'],s['source_path'],'QUALIFIED'):
                raise ValueError('Source catalog identity conflict')
            stored=json.loads(catalog[3])
            expected=next(p for p in profiles if p['source_key']==s['source_key'])
            if stored!=expected:raise ValueError('Source catalog/profile conflict')
            row=db.execute('SELECT bid,environment,signal,records,payload FROM blocks WHERE source_key=? ORDER BY bid LIMIT 1',(s['source_key'],)).fetchone()
            if row is None:
                reports.append({**s,'status':'NO_RETAINED_BLOCK'});continue
            bid,environment,signal,record_count,payload=row
            if (environment,signal)!=(s['scenario'],'metric'):raise ValueError('Block scope conflict')
            rows=bounded_inflate(payload)
            if record_count!=len(rows):raise ValueError('Block row accounting conflict')
            sample=rows[:256]
            grouped=defaultdict(list)
            missing_identity=0
            for ns,line,state,error,raw in sample:
                if state!='mapped':continue
                component=raw.get('cmdb_id') or raw.get('service') or raw.get('tc') or raw.get('serviceName')
                if not component:missing_identity+=1;continue
                values=[(raw.get('kpi_name',raw.get('name')),raw.get('value'))] if 'value' in raw else [(k,raw.get(k)) for k in s['metric_names']]
                for name,value in values:
                    if name in s['metric_names']:grouped[(component,name)].append((ns,value))
            summaries=[]
            for (component,name),items in sorted(grouped.items()):
                finite=[];missing=0;invalid=0
                for ns,value in items:
                    if value is None or value=='':missing+=1;continue
                    try:
                        number=Decimal(value)
                        if not number.is_finite():invalid+=1
                        else:finite.append(number)
                    except (InvalidOperation,ValueError,TypeError):invalid+=1
                times=sorted({t for t,v in items})
                deltas=Counter(str(b-a) for a,b in zip(times,times[1:]))
                summaries.append({'source_component_identity':component,'metric_name':name,'observations_in_sample':len(items),'missing_values_in_sample':missing,'invalid_numeric_values_in_sample':invalid,'distinct_finite_values':len(set(finite)),'min_raw_numeric':str(min(finite)) if finite else None,'max_raw_numeric':str(max(finite)) if finite else None,'first_observed_ns':times[0] if times else None,'last_observed_ns':times[-1] if times else None,'observed_unique_timestamp_spacing_ns':dict(deltas),'unit':'UNKNOWN','temporality':'UNKNOWN','reset_policy':'UNKNOWN','normality':'UNKNOWN','spacing_interpretation':'Observed spacing only; not certified cadence or independent control exposure'})
            report={**s,'status':'INSPECTED','block_id':bid,'block_payload_sha256':sha(payload),'compressed_bytes':len(payload),'decoded_rows':len(rows),'inspected_rows':len(sample),'state_counts':dict(Counter(r[2] for r in sample)),'sample_first_timestamp_ns':min(r[0] for r in sample) if sample else None,'sample_last_timestamp_ns':max(r[0] for r in sample) if sample else None,'missing_identity_rows':missing_identity,'selected_names_observed':sorted({x['metric_name'] for x in summaries}),'selected_names_not_observed':[m for m in s['metric_names'] if m not in {x['metric_name'] for x in summaries}],'series_summaries':summaries,'health_labels':'NONE_ACQUIRED','population':'Inherited fault-centered retained context; not certified healthy or independent'}
            reports.append(report);samples.append((bid,sha(payload)))
        for bid,digest in samples:
            payload=db.execute('SELECT payload FROM blocks WHERE bid=?',(bid,)).fetchone()[0]
            if sha(payload)!=digest:raise ValueError('Sample block changed')
    finally:
        db.close()
    after=dbpath.stat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise ValueError('Retained DB stat changed')
    if any(sha((ROOT/p).read_bytes())!=h for p,h in profile_hashes.items()):raise ValueError('Profiles changed')
    result={'scope':'Read-only descriptive evidence acquisition; no detector, threshold or new scientific execution','sample_plan_sha256':sha(plan_path.read_bytes()),'reports':reports,'totals':{'selected_sources':len(selected),'blocks_read':len(samples),'decoded_rows':sum(r.get('decoded_rows',0) for r in reports),'inspected_rows':sum(r.get('inspected_rows',0) for r in reports),'series_summarized':sum(len(r.get('series_summaries',[])) for r in reports)},'preservation':{'profile_hashes_unchanged':True,'sampled_block_hashes_unchanged':True,'db_size_mtime_unchanged':True,'full_database_hash_reverified':False},'normal_controls':'NOT ESTABLISHED','independent_holdout':'NOT ESTABLISHED','raw_dataset_accessed':False,'labels_read_by_sampler':False,'experiment_registered':False,'experiment_executed':False}
    with result_path.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False)
    print(json.dumps(result['totals']))


if __name__=='__main__':main()
