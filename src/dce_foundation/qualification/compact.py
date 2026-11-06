"""Lossless per-source compressed row blocks; immutable source pointers preserved."""
from collections import Counter
import json
import sqlite3
import zlib
from ..domain import canonical_json,digest


SCHEMA='''CREATE TABLE blocks(bid INTEGER PRIMARY KEY,source_key TEXT,environment TEXT,signal TEXT,min_ns INTEGER,max_ns INTEGER,records INTEGER,payload BLOB);
CREATE TABLE sources(source_key TEXT PRIMARY KEY,environment TEXT,path TEXT,status TEXT,report TEXT);'''


class BlockWriter:
    def __init__(self,db):
        self.db=db
        self.key=None
        self.records=[]
        self.raw_bytes=0
        self.total=0

    def flush(self):
        if not self.records:
            return
        key,env,signal=self.key
        times=[r[0] for r in self.records]
        body=canonical_json(self.records).encode()
        self.db.execute('INSERT INTO blocks(source_key,environment,signal,min_ns,max_ns,records,payload) VALUES (?,?,?,?,?,?,?)',
                        (key,env,signal,min(times),max(times),len(times),zlib.compress(body,6)))
        self.total+=len(times)
        self.records=[]
        self.raw_bytes=0

    def execute(self,sql,params=()):
        if sql.startswith('INSERT INTO context'):
            oid,key,line,ns,env,signal,resource,state,error,payload=params
            current=(key,env,signal)
            if current!=self.key:
                self.flush()
                self.key=current
            raw_body=zlib.decompress(payload)
            self.records.append([ns,line,state,error,json.loads(raw_body)])
            self.raw_bytes+=len(raw_body)
            if len(self.records)>=1024 or self.raw_bytes>=4*1024*1024:
                self.flush()
            return None
        self.flush()
        return self.db.execute(sql,params)

    def commit(self):
        self.flush()
        self.db.commit()


def block_rows(db,scenario,start,end,include_rejected=False):
    cursor=db.execute('SELECT b.source_key,b.environment,b.signal,b.payload,s.status FROM blocks b JOIN sources s ON s.source_key=b.source_key WHERE b.environment=? AND b.min_ns<=? AND b.max_ns>=? ORDER BY b.bid',
                      (scenario,end,start))
    for key,environment,signal,payload,source_status in cursor:
        for ns,line,state,error,raw in json.loads(zlib.decompress(payload)):
            if not start<=ns<=end:
                continue
            if source_status!='QUALIFIED':
                state='source_unqualified'
            if not include_rejected and state!='mapped':
                continue
            yield 'row:'+digest([key,line]),ns,signal,environment,raw,state,error


def projected_context_rows(db,scenario,start,end):
    for oid,ns,signal,environment,raw,state,error in block_rows(db,scenario,start,end):
        yield oid,ns,signal,environment,raw


def compact_coverage(db,labels,links,config):
    linked={}
    for link in links:
        if link['status']=='QUALIFIED':
            for iid in link['incident_ids']:
                linked.setdefault(iid,[]).append(link['query_id'])
    reports=[]
    for label in labels:
        t=label['fault_ns']
        a,b=t-config['incident_before_seconds']*10**9,t+config['incident_after_seconds']*10**9
        counts,root=Counter(),Counter()
        resources=set()
        for oid,ns,signal,environment,raw,state,error in block_rows(db,label['scenario'],a,b,True):
            counts['selected_rows']+=1
            counts[state]+=1
            if state!='mapped':
                continue
            name=raw.get('cmdb_id') or raw.get('service') or raw.get('tc') or raw.get('serviceName')
            segment='before' if ns<t else ('at_fault' if ns==t else 'after')
            counts[segment]+=1
            if name:
                resources.add(name)
            counts['spans' if signal=='span' else signal]+=1
            if name==label['raw']['component']:
                root[segment]+=1
                root[signal]+=1
        found=sum(root[s] for s in ('before','at_fault','after'))>0
        reports.append({'incident_id':label['incident_id'],'scenario':label['scenario'],'root_entity':label['raw']['component'],
            'fault_time_ns':t,'retrieval_window_ns':[a,b],'inference_window_ns':[a,t],
            'telemetry_available_before':counts['before'],'telemetry_available_at_fault':counts['at_fault'],'telemetry_available_after':counts['after'],
            'root_observation_found':found,'root_trace_found':root['span']>0,
            'root_service_found':'UNKNOWN; exact resource presence is not service alias proof',
            'root_counts':dict(root),'candidate_resources':len(resources),'candidate_spans':counts['spans'],
            'query_association':'QUALIFIED' if label['incident_id'] in linked else 'UNKNOWN',
            'associated_queries':linked.get(label['incident_id'],[]),'counts':dict(counts),
            'coverage_status':'ROOT_OBSERVED' if found else ('OTHER_TELEMETRY_ONLY' if counts['mapped'] else 'NO_MAPPED_TELEMETRY'),
            'label_validity':'not judged from telemetry presence','before_only_task_eligible':root['before']+root['at_fault']>0})
    return reports


def inherit_complete_files(old_path,new_db,output):
    from ..representation_v2.audit import write_new
    from ..inspection import file_hash
    profiles=[]
    manifest=[]
    writer=BlockWriter(new_db)
    old=sqlite3.connect('file:'+str((old_path/'context.sqlite').resolve())+'?mode=ro',uri=True)
    for file in sorted(old_path.glob('file-*.json')):
        profile=json.loads(file.read_text())
        key=profile['source_key']
        rows=0
        for record in old.execute('SELECT oid,source_key,source_row,event_ns,environment,signal,resource_raw,state,error,payload FROM context WHERE source_key=?',(key,)):
            writer.execute('INSERT INTO context',record)
            rows+=1
        writer.commit()
        expected=sum(profile['selection_counts'].get(s,0) for s in ('mapped','rejected','ambiguous','out_of_window','unsupported'))
        if rows!=expected:
            raise ValueError('inherited context does not conserve completed-file selection')
        new_db.execute('INSERT INTO sources VALUES (?,?,?,?,?)',(key,profile['scenario'],profile['path'],profile['decision'],canonical_json(profile)))
        profiles.append(profile)
        write_new(output/f'file-{len(profiles):03d}.json',profile)
        manifest.append({'source_profile':str(file),'source_profile_sha256':file_hash(file),'decompressed_sha256':profile['decompressed_sha256'],
                         'rows_transferred':rows,'crc_eof_verified':profile['crc_eof_verified']})
    old.close()
    new_db.commit()
    write_new(output/'inherited-complete-files.json',manifest)
    return profiles
