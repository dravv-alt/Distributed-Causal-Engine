"""Independent semantic oracles for E003-AM001; source labels are external."""
from dataclasses import asdict
import io
import sqlite3
import zipfile
import pytest
from dce_foundation.domain import canonical_json, digest
from dce_foundation.representation_v2.timestamps import epoch_ns, profile, classify, day_bounds
from dce_foundation.representation_v2.model import (SourceRef, ResourceKind, resource,
    MetricRegistry, MetricSemantics, QueryWindow, Dependency, Relation)
from dce_foundation.representation_v2.openrca import map_record, inference_view
from dce_foundation.representation_v2.store import new_store, canonical_digest
from dce_foundation.representation_v2.topology import resolve_trace_context, typed_graph, workbook_topology

START, END = day_bounds('2021_03_25')
SECONDS = str(START // 10**9 + 120)


@pytest.mark.parametrize('unit,multiplier',[('s',1),('ms',1000),('us',10**6),('ns',10**9)])
def test_time_scale_requires_source_date(unit,multiplier):
    value = str(int(SECONDS) * multiplier)
    result = profile([value,value],START,END)
    assert result['selected_unit'] == unit
    assert epoch_ns(value,unit) == int(SECONDS)*10**9
    wrong_day = profile([value],*day_bounds('2022_03_25'))
    assert wrong_day['selected_unit'] is None


def test_mixed_invalid_and_out_of_window_are_distinct():
    assert profile([SECONDS,str(int(SECONDS)*1000)],START,END)['status'] == 'ambiguous'
    assert profile(['NaN',''],START,END)['status'] == 'invalid'
    p = profile([SECONDS],START,END)
    assert classify('NaN',p,START,END) == ('rejected',None)
    assert classify(str(int(SECONDS)+86400),p,START,END) == ('out_of_window',None)
    assert classify(str(int(SECONDS)*1000),p,START,END) == ('ambiguous',None)
    with pytest.raises(ValueError):
        epoch_ns(SECONDS+'.0000000001','s')


@pytest.mark.parametrize('kind',list(ResourceKind))
def test_resource_kind_preserves_identity(kind):
    ref = SourceRef('fixture','key',2,{'name':'db-1'})
    r = resource('environment-a','db-1',ref,kind,aliases=('reviewed-old-name',))
    assert r.source_name == 'db-1'
    assert r.resource_kind == kind
    assert r.aliases == ('reviewed-old-name',)
    assert r.resource_id != resource('environment-b','db-1',ref).resource_id
    with pytest.raises(ValueError):
        resource('environment-a',' db-1',ref)


@pytest.mark.parametrize('kind,temporality,unit',[('GAUGE','INSTANTANEOUS','bytes'),('COUNTER','CUMULATIVE','count'),('DURATION','UNKNOWN','ms')])
def test_metric_registry_requires_evidence(kind,temporality,unit):
    reg = MetricRegistry()
    entry = MetricSemantics('m','source_m','fixture',unit,temporality,'NONE',kind,
                            provenance=SourceRef('spec','document',1,{'unit':unit}))
    reg.register(entry)
    assert reg.lookup('fixture','source_m') == entry
    assert reg.lookup('other','source_m').unit == 'UNKNOWN'
    with pytest.raises(ValueError):
        reg.register(MetricSemantics('m','m','fixture',unit='ms'))


def test_exact_strings_and_wide_mapping_with_no_guessed_semantics():
    row = {'timestamp':SECONDS,'rr':'0.0000000000000000000000123','sr':'1','cnt':'7','mrt':'8','tc':'server'}
    p = profile([SECONDS],START,END)
    state, obs, res, error = map_record('Bank','Bank/telemetry/2021_03_25/metric/metric_app.csv',2,row,p,START,END)
    assert state == 'mapped' and len(obs) == 4
    assert {o.metric.metric_name for o in obs} == {'rr','sr','cnt','mrt'}
    assert next(o for o in obs if o.metric.metric_name=='rr').value == row['rr']
    assert all(o.metric.unit == 'UNKNOWN' and o.metric.temporality == 'UNKNOWN' for o in obs)
    assert all(o.provenance.attributes == row for o in obs)
    assert res.resource_kind == ResourceKind.UNKNOWN
    assert digest([asdict(o) for o in obs]) == digest([asdict(o) for o in map_record('Bank',
        'Bank/telemetry/2021_03_25/metric/metric_app.csv',2,row,p,START,END)[1]])


def test_inference_projection_excludes_raw_and_future_information():
    row = {'timestamp':SECONDS,'cmdb_id':'server','log_id':'root-is-db','log_name':'fault-injection',
           'value':'The injected root is DB (answer-bearing text)'}
    p = profile([SECONDS],START,END)
    o = map_record('Bank','Bank/telemetry/2021_03_25/log/log_service.csv',2,row,p,START,END)[1][0]
    view = inference_view(o,QueryWindow(START,END))
    text = canonical_json(view)
    assert 'root-is-db' not in text and 'fault-injection' not in text and 'answer-bearing' not in text
    assert 'source_key' not in text and 'provenance' not in text and 'Bank/' not in text
    assert inference_view(o,QueryWindow(START,int(SECONDS)*10**9-1)) is None


def test_trace_context_no_cross_trace_or_self_parent_edges(tmp_path):
    with new_store(tmp_path/'trace.sqlite') as db:
        fixture = [('p','env','t','p',None,'A',1,'k',2),('c','env','t','c','p','B',2,'k',3),
                   ('self','env','t','self','self','C',3,'k',4),('missing','env','t2','x','p','D',4,'k',5),
                   ('dup1','env','t','dup',None,'E',5,'k',6),('dup2','env','t','dup',None,'E',5,'k',7),
                   ('amb','env','t','amb','dup','F',6,'k',8)]
        db.executemany('INSERT INTO spans VALUES (?,?,?,?,?,?,?,?,?)',fixture)
        counts = resolve_trace_context(db)
        assert counts['resolved_parent'] == 1
        assert counts['self_parent_convention_unknown'] == 1
        assert counts['unresolved_parent'] == 1
        assert counts['ambiguous_parent'] == 1
        assert db.execute('SELECT count(*) FROM dependencies').fetchone()[0] == 1
        body = __import__('json').loads(db.execute('SELECT body FROM dependencies').fetchone()[0])
        assert body['source'] == 'A' and body['target'] == 'B'
    with pytest.raises(FileExistsError):
        with new_store(tmp_path/'trace.sqlite'):
            pass


@pytest.mark.parametrize('relation',[Relation.CALLS,Relation.RUNS_ON,Relation.DEPENDS_ON])
def test_graph_types_require_evidence(relation):
    ref = SourceRef('fixture','k',2,{})
    a,b = resource('env','A',ref),resource('env','B',ref)
    d = Dependency('d',a.resource_id,b.resource_id,relation,('source-cell',),ref)
    graph = typed_graph([a,b],[d])
    assert graph[a.resource_id][b.resource_id]['d']['relation_type'] == relation.value
    with pytest.raises(ValueError):
        typed_graph([a,b],[Dependency('d',a.resource_id,b.resource_id,relation,(),ref)])
    assert not any('CAUSAL' in e['relation_type'] for _,_,e in graph.edges(data=True))


def test_workbook_merge_cells_only_propagate_inside_declared_ranges():
    ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    def row(n,values):
        return '<row r="'+str(n)+'">'+''.join('<c r="'+c+str(n)+'" t="inlineStr"><is><t>'+v+'</t></is></c>' for c,v in values.items())+'</row>'
    xml = '<worksheet xmlns="'+ns+'"><sheetData>'+row(1,dict(zip('ABCDE',['Type','Number','Host','Name','From (containers)'])))
    xml += row(2,{'A':'redis','C':'host','D':'cache1'})+row(3,{'D':'cache2'})+row(4,{'D':'unknown'})+row(5,{'D':'host','A':'unrecognized-os-type'})
    xml += '</sheetData><mergeCells><mergeCell ref="A2:A3"/><mergeCell ref="C2:C3"/></mergeCells></worksheet>'
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer,'w') as z:
        z.writestr('xl/worksheets/sheet1.xml',xml)
    resources,deps,report = workbook_topology(buffer.getvalue(),'wb')
    assert len(deps) == 2
    assert sum(r.resource_kind == ResourceKind.CACHE for r in resources.values()) == 2
    assert next(r for r in resources.values() if r.source_name=='unknown').resource_kind == ResourceKind.UNKNOWN
    assert next(r for r in resources.values() if r.source_name=='host').resource_kind == ResourceKind.HOST
    assert len(typed_graph(resources.values(),deps).edges) == 2


def test_partial_invalid_metric_row_is_atomic():
    row = {'timestamp':SECONDS,'rr':'1','sr':'BAD','cnt':'7','mrt':'8','tc':'server'}
    state, obs, res, error = map_record('Bank','metric_app.csv',2,row,profile([SECONDS],START,END),START,END)
    assert state == 'rejected' and obs == [] and res is None


def test_missing_service_trace_retains_unresolved_semantics():
    row = dict(timestamp=str(int(SECONDS)*1000),cmdb_id='pod',parent_id='self',span_id='self',trace_id='t',duration='5')
    state,obs,_,_ = map_record('Bank','trace_span.csv',2,row,profile([row['timestamp']],START,END),START,END)
    assert state == 'mapped'
    assert obs[0].service is None and obs[0].end_ns is None
    assert obs[0].duration_raw == '5' and obs[0].duration_unit == 'UNKNOWN'


def test_cross_system_disk_pipeline_conservation_and_repeatability(tmp_path):
    from dce_foundation.representation_v2.audit import telemetry_pass
    root = tmp_path / 'data'
    output = tmp_path / 'output'
    root.mkdir()
    output.mkdir()
    for system in ('Bank','Market','Telecom'):
        scenarios = ['Market/cloudbed-1','Market/cloudbed-2'] if system=='Market' else [system]
        with zipfile.ZipFile(root/(system+'.zip'),'w') as z:
            for scenario in scenarios:
                if system=='Telecom':
                    header = 'itemid,name,bomc_id,timestamp,value,cmdb_id\n'
                    row = 'i,metric,b,'+str(int(SECONDS)*1000)+',42,r\n'
                else:
                    header = 'timestamp,cmdb_id,kpi_name,value\n'
                    row = SECONDS+',r,metric,42\n'
                z.writestr(scenario+'/telemetry/2021_03_25/metric/metric_container.csv',header+row+row)
    config = {'rows_per_telemetry_file':512,'profiling_boundary_allowance_seconds':3600,'timestamp_minimum_support':0.99}
    one,two = telemetry_pass(root,output,config,1),telemetry_pass(root,output,config,2)
    assert one['canonical_sha256'] == two['canonical_sha256']
    assert one['graph_sha256'] == two['graph_sha256']
    assert one['observations'] == 8
    assert all(f['row_conservation'] and f['counts']['duplicates']==1 and not f['truncated'] for f in one['files'])
    with sqlite3.connect(output/'operational-001.sqlite') as db:
        assert db.execute('SELECT count(*) FROM observations').fetchone()[0]==8
        assert db.execute('SELECT count(*) FROM dispositions').fetchone()[0]==8
