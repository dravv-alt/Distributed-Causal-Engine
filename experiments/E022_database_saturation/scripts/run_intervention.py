from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import sys
import time

import httpx
import numpy as np
from opentelemetry.proto.collector.metrics.v1 import metrics_service_pb2
from opentelemetry.proto.common.v1 import common_pb2
from opentelemetry.proto.metrics.v1 import metrics_pb2
from opentelemetry.proto.resource.v1 import resource_pb2

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"experiments/E022_database_saturation"
RUN=BASE/"results/E022-R001"
sys.path.insert(0,str(ROOT/"src"))
from dce_foundation.ingest.app import PROTOBUF_CONTENT_TYPE, create_app


def payload(trial:int)->bytes:
    request=metrics_service_pb2.ExportMetricsServiceRequest()
    rm=request.resource_metrics.add(resource=resource_pb2.Resource(attributes=[common_pb2.KeyValue(key="service.name",value=common_pb2.AnyValue(string_value="saturation-probe"))]))
    sm=rm.scope_metrics.add();metric=sm.metrics.add(name="synthetic.write.probe",unit="1")
    point=metric.sum.data_points.add(as_int=trial+1,time_unix_nano=1_800_000_000_000_000_000+trial)
    point.attributes.add(key="trial.id",value=common_pb2.AnyValue(string_value=f"trial-{trial:02d}"))
    metric.sum.aggregation_temporality=metrics_pb2.AGGREGATION_TEMPORALITY_CUMULATIVE
    metric.sum.is_monotonic=True
    return request.SerializeToString()


async def send(app,data):
    transport=httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport,base_url="http://dce.local") as client:
        start=time.perf_counter()
        response=await client.post("/v1/metrics",content=data,headers={"content-type":PROTOBUF_CONTENT_TYPE})
        return response.status_code,round((time.perf_counter()-start)*1000,3),response.content.hex()


def main():
    RUN.mkdir(parents=True,exist_ok=True)
    db=RUN/"intake.sqlite3"
    if db.exists():raise SystemExit("refusing to overwrite existing run database")
    app=create_app(db)
    outcomes=[]
    for trial in range(5):
        data=payload(trial);digest=hashlib.sha256(data).hexdigest()
        c_status,c_ms,c_body=asyncio.run(send(app,data))
        lock=sqlite3.connect(db,timeout=0,isolation_level=None)
        lock.execute("BEGIN IMMEDIATE")
        try:
            l_status,l_ms,l_body=asyncio.run(send(app,data))
        finally:
            lock.execute("ROLLBACK");lock.close()
        r_status,r_ms,r_body=asyncio.run(send(app,data))
        rows=app.state.store.replay(include_payload=True)
        matches=[row for row in rows if row.payload_sha256==digest]
        outcomes.append({"trial":trial,"payload_sha256":digest,"control":{"status":c_status,"elapsed_ms":c_ms,"response_hex":c_body},"locked_intervention":{"status":l_status,"elapsed_ms":l_ms,"response_hex":l_body},"post_release_retry":{"status":r_status,"elapsed_ms":r_ms,"response_hex":r_body},"matching_durable_rows":[{"sequence":row.sequence,"duplicate_of_sequence":row.duplicate_of_sequence,"payload_sha256":row.payload_sha256} for row in matches]})
    result={"experiment":"E022-R001","planning_stage":"XP019","intervention":"hold SQLite BEGIN IMMEDIATE writer lock on same disposable intake database","matched_trials":len(outcomes),"outcomes":outcomes,"final_store_stats":app.state.store.stats(),"runtime":{"python":sys.version,"platform":platform.platform(),"numpy":np.__version__,"network_used":False,"transport":"in-process httpx ASGITransport"}}
    (RUN/"raw-run.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"trials":len(outcomes),"control_statuses":[x["control"]["status"] for x in outcomes],"locked_statuses":[x["locked_intervention"]["status"] for x in outcomes],"retry_statuses":[x["post_release_retry"]["status"] for x in outcomes],"database_rows":app.state.store.stats()["accepted"],"database_bytes":app.state.store.stats()["database_bytes"]},indent=2))


if __name__=="__main__":main()
