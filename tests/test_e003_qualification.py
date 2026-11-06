"""E003-AM002 full-file, temporal leakage, association and replay oracles."""
from collections import Counter
from dataclasses import asdict
from decimal import Decimal
import hashlib
import json
import sqlite3
import zipfile
import pytest
from dce_foundation.domain import canonical_json
from dce_foundation.qualification.time_profile import FullTimeProfile
from dce_foundation.qualification.semantics import MetricQualification
from dce_foundation.qualification.projection import projected_row,query_projection,projection_violations
from dce_foundation.qualification.scan import scan_file
from dce_foundation.qualification.evaluator import associations,parse_query_window
from dce_foundation.qualification.run import replay_cases
from dce_foundation.representation_v2.timestamps import day_bounds

START,END=day_bounds('2021_03_25')
T=START+3600*10**9


@pytest.mark.parametrize('unit,factor',[('s',10**9),('ms',10**6),('us',1000),('ns',1)])
def test_complete_profile_scale_and_late_mixed_row(unit,factor):
    p=FullTimeProfile(START,END)
    for _ in range(600):
        state,ns,selected=p.observe(str(Decimal(T)/factor))
    assert p.report()['decision']=='QUALIFIED'
    assert p.report()['selected_scale']==unit
    other='ms' if unit!='ms' else 's'
    q=10**6 if other=='ms' else 10**9
    p.observe(str(Decimal(T)/q))
    assert p.report()['decision']=='AMBIGUOUS_OR_INVALID'
    assert p.report()['row_conservation']


def test_invalid_boundary_and_neighbor_states():
    p=FullTimeProfile(START,END)
    for value in (str((START-10**9)//10**9),str(T//10**9),str((T-10**9)//10**9),'NaN','not-time'):
        p.observe(value)
    result=p.report()
    assert result['counts']['out_of_window']==1
    assert result['counts']['malformed_rows']==2
    assert result['counts']['out_of_order']==1
    assert result['row_conservation']


def test_metric_unknown_is_valid_but_unsupported_assertion_is_not():
    entry=MetricQualification('cpu','metric_container.csv','Bank')
    assert entry.status=='UNKNOWN' and entry.evidence_source is None
    with pytest.raises(ValueError):
        MetricQualification('cpu','source','Bank',unit='percent')
    known=MetricQualification('x','s','e',kind='GAUGE',evidence_source='reviewed-doc',confidence=1,status='QUALIFIED')
    assert known.kind=='GAUGE'


def test_raw_identifiers_text_and_metadata_never_reach_projection():
    raw={'timestamp':str(T//10**9),'tc':'root-cause-db','rr':'42','reason':'the answer',
         'scoring_points':'injected DB','instruction':'fault query','fault_time':'today'}
    rows=[('answer-bearing-oid',T,'metric','scenario-3',raw)]
    p=query_projection(rows,T-10**9,T)
    text=canonical_json(p)
    for forbidden in ('root-cause-db','the answer','injected DB','fault query','answer-bearing-oid','scenario-3'):
        assert forbidden not in text
    assert len(p['observations'])==1
    assert not projection_violations(p)
    changed={**raw,'reason':'other answer','scoring_points':'other root'}
    assert p==query_projection([('answer-bearing-oid',T,'metric','scenario-3',changed)],T-10**9,T)


def test_parent_after_cutoff_cannot_create_edge():
    def span(s,parent):
        return dict(cmdb_id=s,trace_id='trace',span_id=s,parent_id=parent,timestamp='1',duration='10')
    rows=[('child',T,'span','env',span('c','p')),('parent',T+1,'span','env',span('p',''))]
    cutoff=query_projection(rows,T-1,T)
    assert cutoff['edges']==[] and cutoff['trace_states']['unresolved_parent']==1
    later=query_projection(rows,T-1,T+1)
    assert len(later['edges'])==1
    assert not projection_violations(later)


def test_self_duplicate_missing_parent_and_cross_trace():
    rows=[]
    for i,(trace,span,parent) in enumerate([('t','self','self'),('t','a',''),('t','a',''),('t','child','a'),('other','x','a')]):
        rows.append((str(i),T,'span','env',dict(cmdb_id='r',trace_id=trace,span_id=span,parent_id=parent,duration='1')))
    p=query_projection(rows,T,T)
    assert p['edges']==[]
    assert p['trace_states']['self_parent_convention_unknown']==1
    assert p['trace_states']['ambiguous_parent']==1
    assert p['trace_states']['unresolved_parent']==1


def test_non_numeric_metric_does_not_pass_boundary():
    with pytest.raises(ValueError):
        projected_row('o',T,'metric','env',{'cmdb_id':'r','kpi_name':'m','value':'DB is root'})


def test_query_association_is_not_a_positional_join():
    labels=[{'incident_id':'B@2','scenario':'Bank','fault_ns':T,'raw':{'datetime':'2021-03-25 01:00:00','component':'DB','reason':'overload'}},
            {'incident_id':'B@3','scenario':'Bank','fault_ns':T+3600*10**9,'raw':{'datetime':'2021-03-25 02:00:00','component':'DB','reason':'overload'}}]
    query={'query_id':'q','scenario':'Bank','raw':{'instruction':'On March 25, 2021, between 01:00 and 01:30, find the failure.',
           'scoring_points':'The only predicted root cause component is DB\nThe only predicted root cause reason is overload\n'}}
    match=associations([query],list(reversed(labels)))[0]
    assert match['status']=='QUALIFIED' and match['incident_ids']==['B@2']
    query['raw']['instruction']='Time is not provided'
    assert associations([query],labels)[0]['status']=='UNKNOWN'


def test_parse_window_fails_closed_for_multiple_dates():
    assert parse_query_window('March 25, 2021, 01:00 to 01:30')==(T,T+1800*10**9)
    assert parse_query_window('March 25, 2021 and March 26, 2021 01:00 to 01:30') is None


def test_full_scanner_eof_hash_retrieval_and_late_epoch_change(tmp_path):
    config={'profiling_boundary_allowance_seconds':3600,'minimum_free_disk_bytes':0,'maximum_context_store_bytes':10**9}
    path='Bank/telemetry/2021_03_25/metric/metric_container.csv'
    body='timestamp,cmdb_id,kpi_name,value\n'+''.join(f'{T//10**9+i},root,m,{i}\n' for i in range(700))
    # A row beyond the old 512 cap changes timestamp scale and must fail qualification.
    body+=f'{T//10**6},root,m,1\n'
    archive_path=tmp_path/'Bank.zip'
    with zipfile.ZipFile(archive_path,'w') as z:
        z.writestr(path,body)
    db=sqlite3.connect(tmp_path/'context.sqlite')
    db.executescript('CREATE TABLE context(oid TEXT PRIMARY KEY,source_key TEXT,source_row INTEGER,event_ns INTEGER,environment TEXT,signal TEXT,resource_raw TEXT,state TEXT,error TEXT,payload BLOB);CREATE TABLE sources(source_key TEXT PRIMARY KEY,environment TEXT,path TEXT,status TEXT,report TEXT);')
    with zipfile.ZipFile(archive_path) as z:
        report=scan_file(z,path,'Bank',[(T,T+10**9)],db,config,tmp_path)
    assert report['counts']['rows_seen']==701
    assert report['decision']=='AMBIGUOUS_OR_INVALID'
    assert report['decompressed_sha256']==hashlib.sha256(body.encode()).hexdigest()
    assert report['crc_eof_verified'] and report['row_conservation']
    assert db.execute('SELECT count(*) FROM context').fetchone()[0]==3
    db.close()
