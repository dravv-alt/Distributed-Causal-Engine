import csv
from dataclasses import asdict
import io
import json
from pathlib import Path
import zipfile

import pytest

from dce_foundation.domain import digest, MetricObservation, TraceSpan
from dce_foundation.event_time import normalize_time
from dce_foundation.graph import build_evaluation_graph, graph_dict
from dce_foundation.replay.openrca import replay
from dce_foundation.telemetry.openrca import (OpenRCAAdapter, HEADERS, SCENARIOS,
                                            SchemaError, entity_id)


def csv_text(fields, rows):
    stream=io.StringIO(newline="")
    writer=csv.DictWriter(stream,fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


@pytest.fixture
def dataset(tmp_path):
    records=[dict(level="pod",component="B",timestamp="1614841020",datetime="2021-03-04 14:57:00",reason="fixture fault"),
             dict(level="pod",component="A",timestamp="1614927420",datetime="2021-03-05 14:57:00",reason="second fault")]
    with zipfile.ZipFile(tmp_path/"Bank.zip","w") as z:
        z.writestr("Bank/record.csv",csv_text(records[0].keys(),records))
        z.writestr("Bank/query.csv",csv_text(["task_index","instruction","scoring_points"],
                   [dict(task_index="q1",instruction="find root",scoring_points="SECRET ROOT ANSWER")]))
        for date,second in [("2021_03_04",1614841020),("2021_03_05",1614927420)]:
            metrics=[dict(timestamp=str(second),cmdb_id="B",kpi_name="cpu",value="2.0"),
                     dict(timestamp=str(second),cmdb_id="B",kpi_name="cpu",value="2.0"),
                     dict(timestamp=str(second-1),cmdb_id="A",kpi_name="cpu",value="")]
            z.writestr(f"Bank/telemetry/{date}/metric/metric_container.csv",csv_text(HEADERS["Bank"]["metric_container.csv"],metrics))
            traces=[dict(timestamp=str(second*1000),cmdb_id="A",parent_id="",span_id="a",trace_id="t",duration="3"),
                    dict(timestamp=str(second*1000+1),cmdb_id="B",parent_id="a",span_id="b",trace_id="t",duration="2")]
            z.writestr(f"Bank/telemetry/{date}/trace/trace_span.csv",csv_text(HEADERS["Bank"]["trace_span.csv"],traces))
    return tmp_path


@pytest.mark.parametrize("value,unit,expected",[("1614841020","s",1614841020000000000),
    ("1614841020001","ms",1614841020001000000),("1614841020.125","s",1614841020125000000)])
def test_time_precision(value,unit,expected):
    t=normalize_time(value,"timestamp",unit)
    assert t.epoch_ns==expected
    assert t.source_value==value
    assert t.utc.endswith("Z")


@pytest.mark.parametrize("value",["", "nan", "inf", "garbage", "1614841020.0000000001", "12"])
def test_invalid_times(value):
    with pytest.raises(ValueError): normalize_time(value,"timestamp","s")


def test_no_guessing_units():
    with pytest.raises(ValueError): normalize_time("1614841020","timestamp","UNKNOWN")


def test_identity():
    assert entity_id("Bank","A")!=entity_id("Telecom","A")
    assert entity_id("Bank","a")!=entity_id("Bank","A")
    with pytest.raises(ValueError): entity_id("Bank"," A ")


def test_deterministic_replay(dataset):
    i,g,r=replay(dataset,"Bank@2")
    j,h,s=replay(dataset,"Bank@2")
    assert r==s and graph_dict(g)==graph_dict(h) and i.to_dict()==j.to_dict()
    assert r["record_conservation"] and r["schema"]=="PASS"
    assert r["duplicates_preserved"]==1
    assert r["out_of_order_source_records"]==1
    assert r["missing_metric_values"]==1
    assert len(i.observations)==5


def test_graph_semantics_and_leakage(dataset):
    i,g,r=replay(dataset,"Bank@2")
    calls=[(s,t,a) for s,t,a in g.edges(data=True) if a["relation"]=="CALLS"]
    assert len(calls)==1
    assert calls[0][0]==entity_id("Bank","A") and calls[0][1]==entity_id("Bank","B")
    assert calls[0][2]["evidence_ids"]
    assert "SECRET ROOT ANSWER" not in json.dumps(graph_dict(g))
    assert "fixture fault" not in json.dumps(i.operational_dict())
    evaluation=build_evaluation_graph(i)
    assert evaluation.graph["scope"]=="evaluation_only"
    assert all(a["category"] not in ("possible_causal","established_causal") for _,_,a in g.edges(data=True))
    assert r["ground_truth_roots_observed"]==1


def test_multiple_incidents(dataset):
    a,_,_=replay(dataset,"Bank@2")
    b,_,_=replay(dataset,"Bank@3")
    assert a.start_ns!=b.start_ns
    assert a.ground_truth.events[0].reason=="fixture fault"
    assert b.ground_truth.events[0].reason=="second fault"


def test_bounded_scan_not_adequacy(dataset):
    i,g,r=replay(dataset,"Bank@2",1)
    assert any(s["truncated"] for s in r["file_statistics"].values())
    assert not r["downstream_ready"]


def test_source_fields_preserved(dataset):
    i,_,_=replay(dataset,"Bank@2")
    for o in i.observations:
        expected=HEADERS["Bank"][Path(o.provenance.path).name]
        assert set(o.provenance.attributes)==set(expected)
    for span in (o for o in i.observations if isinstance(o,TraceSpan)):
        assert span.end_time is None and span.duration_unit is None


def test_unsupported_and_malformed(dataset):
    adapter=OpenRCAAdapter(dataset)
    path="Bank/telemetry/2021_03_04/metric/metric_container.csv"
    with pytest.raises(SchemaError): adapter.map_row("Bank",path,2,{"surprise":"x"})
    for value in ("nan","inf","not numeric"):
        with pytest.raises(ValueError):
            adapter.map_row("Bank",path,2,dict(timestamp="1614841020",cmdb_id="A",kpi_name="cpu",value=value))
    with pytest.raises(ValueError): adapter.load("Bank@999")
    with pytest.raises(ValueError): adapter.load("Bank")
    with pytest.raises(ValueError): adapter.load("Bank@2",0)


@pytest.mark.parametrize("system,name",[(s,n) for s,files in HEADERS.items() for n in files])
def test_all_schema_families(system,name,dataset):
    row={k:"1" for k in HEADERS[system][name]}
    for key in ("timestamp","startTime"):
        if key in row: row[key]="1614841020000" if system=="Telecom" or name=="trace_span.csv" else "1614841020"
    for key in ("cmdb_id","service","serviceName","tc"):
        if key in row: row[key]="entity"
    row.update({k:"metric" for k in ("kpi_name","name") if k in row})
    result=OpenRCAAdapter(dataset).map_row(system if system!="Market" else "Market/cloudbed-1",name,2,row)
    assert result
    assert all(o.provenance.attributes==row for o in result)


@pytest.mark.parametrize("scenario",SCENARIOS)
def test_real_archive_sample(scenario):
    root=Path("data/dataset")
    adapter=OpenRCAAdapter(root)
    if not adapter.archive(scenario).exists(): pytest.skip("local immutable OpenRCA archive unavailable")
    iid=adapter.first_incident(scenario)
    incident,graph,report=replay(root,iid,50)
    assert report["record_conservation"]
    assert report["source_rows_mapped"]>0
    assert report["source_rows_rejected"]==0
    assert incident.ground_truth.events
    assert graph.number_of_nodes()>0
    assert report["downstream_ready"] is False
