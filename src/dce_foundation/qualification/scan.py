"""Full timestamp census and union-window retrieval without full canonical expansion."""
import bisect
from collections import Counter
import csv
import gzip
import hashlib
import io
import json
from pathlib import PurePosixPath
import re
import shutil
import time
import zipfile
import zlib
from ..domain import canonical_json,digest
from ..telemetry.openrca import HEADERS
from ..representation_v2.timestamps import day_bounds
from ..representation_v2.openrca import map_record
from .time_profile import FullTimeProfile


class HashingReader(io.RawIOBase):
    def __init__(self,stream):
        self.stream,self.hash,self.bytes=stream,hashlib.sha256(),0
    def readable(self):
        return True
    def readinto(self,b):
        data=self.stream.read(len(b))
        n=len(data)
        b[:n]=data
        self.hash.update(data)
        self.bytes+=n
        return n


def union_windows(windows):
    merged=[]
    for a,b in sorted(windows):
        if merged and a<=merged[-1][1]:
            merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
        else:
            merged.append((a,b))
    return merged


def contains(intervals,starts,ns):
    idx=bisect.bisect_right(starts,ns)-1
    return idx>=0 and ns<=intervals[idx][1]


def scan_file(archive,path,environment,windows,db,config,output):
    started=time.perf_counter()
    info=archive.getinfo(path)
    begin,end=day_bounds(path.split('/telemetry/')[1].split('/')[0])
    time_profile=FullTimeProfile(begin,end,config['profiling_boundary_allowance_seconds'])
    source_key=digest(['OpenRCA',environment,path])
    name=PurePosixPath(path).name
    expected=HEADERS[environment.split('/')[0]][name]
    intervals=union_windows(windows)
    starts=[a for a,b in intervals]
    selected=Counter()
    metrics=Counter()
    missing=Counter()
    cues=Counter()
    last_log=time.monotonic()
    with archive.open(path) as stream:
        hashing=HashingReader(stream)
        text=io.TextIOWrapper(io.BufferedReader(hashing,buffer_size=1024*1024),encoding='utf-8-sig',newline='')
        reader=csv.reader(text)
        header=next(reader)
        if tuple(header)!=expected:
            raise ValueError('unrecognized exact header: '+path)
        field='startTime' if 'startTime' in header else 'timestamp'
        ti=header.index(field)
        metric_index=header.index('kpi_name') if 'kpi_name' in header else (header.index('name') if 'name' in header and name.startswith('metric_') else None)
        wide=[h for h in header if h not in {field,'tc','service','serviceName'}] if name.startswith('metric_') and metric_index is None else []
        signal='span' if name=='trace_span.csv' else ('log' if name.startswith('log_') else 'metric')
        cue_indices=[header.index(k) for k in ('cmdb_id','service','tc','serviceName','kpi_name','name','trace_id','traceId','span_id','id') if k in header]
        cue_pattern=re.compile(r'(?i)(root.?cause|fault.?inject|ground.?truth|scoring.?points|scenario.?\d)')
        quarantine_path=output/'quarantine.jsonl.gz'
        with gzip.open(quarantine_path,'at',encoding='utf-8') as quarantine:
            for line,values in enumerate(reader,2):
                if len(values)!=len(header):
                    value=values[ti] if len(values)>ti else ''
                    state,ns,unit=time_profile.observe(value)
                    selected['shape_errors']+=1
                    quarantine.write(canonical_json({'source_key':source_key,'row':line,'reason':'field_count','raw':values})+'\n')
                    continue
                state,ns,unit=time_profile.observe(values[ti])
                if metric_index is not None:
                    metrics[values[metric_index]]+=1
                for i in cue_indices:
                    value=values[i]
                    # Bound cue-cache memory; counters always count pattern-bearing rows.
                    if cue_pattern.search(value):
                        cues[header[i]]+=1
                if state in ('invalid','malformed','ambiguous','out_of_window'):
                    quarantine.write(canonical_json({'source_key':source_key,'row':line,'reason':state,'timestamp':values[ti]})+'\n')
                if ns is not None and state=='in_window' and contains(intervals,starts,ns):
                    raw=dict(zip(header,values))
                    status,observations,res,error=map_record(environment,path,line,raw,
                        {'selected_unit':unit,'status':'whole_file_pending'},begin,end)
                    selected[status]+=1
                    oid='row:'+digest([source_key,line])
                    resource_raw=(raw.get('cmdb_id') or raw.get('service') or raw.get('tc') or raw.get('serviceName'))
                    payload=zlib.compress(canonical_json(raw).encode(),level=1)
                    db.execute('INSERT INTO context VALUES (?,?,?,?,?,?,?,?,?,?)',
                        (oid,source_key,line,ns,environment,signal,resource_raw,status,error,payload))
                if time_profile.counts['rows_seen']%100000==0:
                    db.commit()
                    if shutil.disk_usage(output).free<config['minimum_free_disk_bytes'] or (output/'context.sqlite').stat().st_size>config['maximum_context_store_bytes']:
                        raise RuntimeError('disk safety limit reached; retained checkpoints; no partial PASS')
                    if time.monotonic()-last_log>20:
                        print(json.dumps({'file':path,'rows':time_profile.counts['rows_seen'],'phase':'streaming'}),flush=True)
                        last_log=time.monotonic()
        # Exhausting the ZipExtFile verifies its ZIP CRC; hash covers decompressed bytes.
        text.close()
        if hashing.bytes!=info.file_size:
            raise ValueError('decompressed size mismatch')
    report=time_profile.report()
    report.update(path=path,source_key=source_key,scenario=environment,header=header,
        expanded_bytes=info.file_size,compressed_bytes=info.compress_size,decompressed_sha256=hashing.hash.hexdigest(),
        crc_eof_verified=True,selection_counts=dict(selected),metric_counts=dict(metrics),
        source_identifier_cue_counts=dict(cues),elapsed_seconds=time.perf_counter()-started)
    if wide:
        report['metric_counts']={h:report['counts']['rows_seen']-selected['shape_errors'] for h in wide}
    db.execute('INSERT INTO sources VALUES (?,?,?,?,?)',(source_key,environment,path,report['decision'],canonical_json(report)))
    db.commit()
    return report
