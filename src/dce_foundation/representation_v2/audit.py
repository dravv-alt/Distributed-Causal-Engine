"""E003-AM001 bounded cross-corpus validation CLI; refuses artifact overwrites."""
import argparse
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone, timedelta
import csv
import hashlib
import importlib.metadata
import io
import itertools
import json
from pathlib import Path, PurePosixPath
import platform
import sqlite3
import subprocess
import sys
import time
import zipfile

from ..domain import canonical_json, digest
from ..inspection import file_hash
from ..telemetry.openrca import SCENARIOS, LABEL_HEADERS
from . import VERSION
from .model import SourceRef, FaultEvent, GroundTruth, Incident
from .openrca import map_record
from .store import new_store, add_resource, canonical_digest
from .timestamps import day_bounds, profile, epoch_ns
from .topology import workbook_topology, resolve_trace_context


def write_new(path, data):
    with Path(path).open("x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n")


def csv_rows(z, path):
    with z.open(path) as f:
        reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline=""))
        header = reader.fieldnames
        if not header or len(set(header)) != len(header):
            raise ValueError("empty or duplicate CSV header")
        yield header
        yield from enumerate(reader, 2)


def peak_memory_bytes():
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes
        class Info(ctypes.Structure):
            _fields_ = [("cb",wintypes.DWORD),("PageFaultCount",wintypes.DWORD)] + [
                (x,ctypes.c_size_t) for x in ("PeakWorkingSetSize","WorkingSetSize","QuotaPeakPagedPoolUsage",
                "QuotaPagedPoolUsage","QuotaPeakNonPagedPoolUsage","QuotaNonPagedPoolUsage","PagefileUsage","PeakPagefileUsage")]
        info = Info()
        info.cb = ctypes.sizeof(info)
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE,ctypes.POINTER(Info),wintypes.DWORD]
        if psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ctypes.byref(info),info.cb):
            return info.PeakWorkingSetSize
        return None
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024)


def snapshot_before_execution(repo, output, config_path):
    paths = list((repo / "src/dce_foundation/representation_v2").glob("*.py"))
    paths += [repo / "tests/test_representation_v2.py",config_path,config_path.parent / "protocol.md"]
    hashes = {p.relative_to(repo).as_posix():file_hash(p) for p in paths}
    with zipfile.ZipFile(output / "source-snapshot.zip", "x", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(paths):
            z.write(p,p.relative_to(repo).as_posix())
    historic = {}
    for folder in ("experiments/E001", "experiments/E002", "experiments/E003_domain_model_adequacy/results/E003-R001"):
        for p in (repo / folder).rglob("*"):
            if p.is_file():
                historic[p.relative_to(repo).as_posix()] = file_hash(p)
    write_new(output / "preflight.json", {
        "created_at_utc":datetime.now(timezone.utc).isoformat(), "git_commit":subprocess.check_output(
            ["git","rev-parse","HEAD"],cwd=repo,text=True).strip(),
        "git_status":subprocess.check_output(["git","status","--short"],cwd=repo,text=True).splitlines(),
        "source_hashes":hashes,"source_snapshot_sha256":file_hash(output / "source-snapshot.zip"),
        "historical_record_hashes":historic, "configuration":json.loads(config_path.read_text()),
        "dataset_manifest_sha256":file_hash(repo / "data/manifests/openrca.json"),
        "python":sys.version,"executable":sys.executable,"platform":platform.platform(),
        "processor":platform.processor(),"dependencies":{n:importlib.metadata.version(n) for n in ("networkx","pytest")}})


def telemetry_pass(root, output, config, repeat):
    reports = []
    start_clock = time.perf_counter()
    db_path = output / f"operational-{repeat:03d}.sqlite"
    with new_store(db_path) as db:
        for scenario in SCENARIOS:
            with zipfile.ZipFile(root / (scenario.split('/')[0] + ".zip")) as z:
                paths = sorted(i for i in z.namelist() if i.startswith(scenario + "/telemetry/") and i.endswith('.csv'))
                for path in paths:
                    started = time.perf_counter()
                    info = z.getinfo(path)
                    date = path.split('/telemetry/')[1].split('/')[0]
                    begin, end = day_bounds(date)
                    rows = csv_rows(z,path)
                    header = next(rows)
                    sample = list(itertools.islice(rows,config["rows_per_telemetry_file"]))
                    field = "startTime" if "startTime" in header else "timestamp"
                    evidence = profile([r.get(field,"") for _,r in sample],begin,end,
                                       config["profiling_boundary_allowance_seconds"],config["timestamp_minimum_support"])
                    key = digest(["OpenRCA",scenario,path])
                    db.execute("INSERT INTO sources VALUES (?,?,?,?,?)",(key,path,scenario,canonical_json(header),canonical_json(evidence)))
                    # Read one additional logical record to distinguish EOF from the configured cap.
                    further = next(rows,None)
                    rows.close()
                    stats = Counter()
                    missing = Counter()
                    minimum, maximum = None, None
                    for line,row in sample:
                        stats['scanned'] += 1
                        missing.update(str(k) for k,v in row.items() if v in (None,""))
                        fingerprint = digest(row)
                        duplicate = db.execute("INSERT OR IGNORE INTO fingerprints VALUES (?,?)",(key,fingerprint)).rowcount == 0
                        stats['duplicates'] += int(duplicate)
                        state, obs, res, error = map_record(scenario,path,line,row,evidence,begin,end)
                        stats[state] += 1
                        db.execute("INSERT INTO dispositions VALUES (?,?,?,?,?)",(key,line,state,error,canonical_json(row)))
                        if state == 'mapped':
                            add_resource(db,res)
                            for o in obs:
                                db.execute("INSERT INTO observations VALUES (?,?,?,?,?,?)",(o.object_id,o.event_ns,key,line,o.resource_id,canonical_json(asdict(o))))
                                minimum = o.event_ns if minimum is None else min(minimum,o.event_ns)
                                maximum = o.event_ns if maximum is None else max(maximum,o.event_ns)
                                stats[o.signal + '_observations'] += 1
                                if o.signal == 'span':
                                    db.execute("INSERT INTO spans VALUES (?,?,?,?,?,?,?,?,?)",(o.object_id,scenario,o.trace_id,o.span_id,
                                        o.parent_span_id,o.resource_id,o.event_ns,key,line))
                                    stats['missing_service'] += o.service is None
                                    stats['missing_type'] += not (row.get('type') or row.get('callType'))
                    scoped_resources = db.execute("SELECT count(DISTINCT resource_id) FROM observations WHERE source_key=?",(key,)).fetchone()[0]
                    traces = db.execute("SELECT count(DISTINCT trace_id) FROM spans WHERE source_key=?",(key,)).fetchone()[0]
                    reports.append({"system":scenario,"path":path,"source_key":key,"file_size":info.file_size,
                        "compressed_size":info.compress_size,"zip_crc32":f"{info.CRC:08x}","header":header,
                        "timestamp_profile":evidence,"counts":dict(stats),"missingness":dict(missing),
                        "full_file_row_count":len(sample) if further is None else None,"truncated":further is not None,
                        "sample_strategy":"first 512 logical records; not random or incident representative",
                        "timestamp_range_ns":[minimum,maximum],"resource_count":scoped_resources,"trace_count":traces,
                        "elapsed_seconds":time.perf_counter()-started,
                        "row_conservation":stats['scanned'] == sum(stats[x] for x in ('mapped','rejected','ambiguous','out_of_window','unsupported'))})
                    db.commit()
        workbook_report = None
        for archive in sorted(root.glob('*.zip')):
            if archive.name in ('Bank.zip','Market.zip','Telecom.zip'):
                continue
            with zipfile.ZipFile(archive) as z:
                for path in sorted(n for n in z.namelist() if n.endswith('AppTelecomDeploymentList.xlsx')):
                    key = digest([archive.name,path])
                    resources,deps,workbook_report = workbook_topology(z.read(path),key)
                    db.execute("INSERT INTO sources VALUES (?,?,?,?,?)",(key,archive.name+'!'+path,'Telecom','[]','{}'))
                    for r in resources.values():
                        add_resource(db,r)
                    for d in deps:
                        db.execute("INSERT INTO dependencies VALUES (?,?,?,?)",(d.dependency_id,d.event_ns,d.relation_type.value,canonical_json(asdict(d))))
        traces = resolve_trace_context(db)
        import networkx as nx
        graph = nx.MultiDiGraph(schema_version=VERSION, epistemic_status='OBSERVED')
        for rid, body in db.execute('SELECT resource_id,body FROM resources ORDER BY resource_id'):
            r = json.loads(body)
            graph.add_node(rid,node_type='Resource',resource_kind=r['resource_kind'])
        for did, body in db.execute('SELECT did,body FROM dependencies ORDER BY did'):
            d = json.loads(body)
            if d['source'] not in graph or d['target'] not in graph or not d['evidence']:
                raise ValueError('graph edge lacks operational resource/evidence')
            graph.add_edge(d['source'],d['target'],key=did,relation_type=d['relation_type'],
                           epistemic_status=d['epistemic_status'],evidence=d['evidence'])
        graph_payload = {'nodes':sorted(({'id':n,**a} for n,a in graph.nodes(data=True)),key=lambda x:x['id']),
                         'edges':sorted(({'source':a,'target':b,'id':k,**v} for a,b,k,v in graph.edges(keys=True,data=True)),key=lambda x:x['id'])}
        write_new(output / f'graph-{repeat:03d}.json',graph_payload)
        checksum = canonical_digest(db)
        summary = {"canonical_sha256":checksum,"graph_sha256":digest(graph_payload),"observations":db.execute("SELECT count(*) FROM observations").fetchone()[0],
                   "resources":db.execute("SELECT count(*) FROM resources").fetchone()[0],
                   "dependencies_by_type":dict(db.execute("SELECT relation_type,count(*) FROM dependencies GROUP BY relation_type")),
                   "resource_kinds":dict(Counter(json.loads(b)["resource_kind"] for (b,) in db.execute("SELECT body FROM resources"))),
                   "trace_parent_states":traces,"workbook":workbook_report,"files":reports}
    summary['performance'] = {"elapsed_seconds":time.perf_counter()-start_clock,"peak_working_set_bytes":peak_memory_bytes(),
        "scanned_rows_per_second":sum(r['counts']['scanned'] for r in reports)/(time.perf_counter()-start_clock),
        "sqlite_bytes":db_path.stat().st_size,"memory_scope":"process high-water mark; not incremental per file"}
    write_new(output / f"coverage-{repeat:03d}.json",summary)
    return summary


def evaluation_only(root, output):
    database = output / "evaluation-only.sqlite"
    if database.exists():
        raise FileExistsError(database)
    faults, issues, queries, incident_checks = [], [], [], []
    with sqlite3.connect(database) as db:
        db.execute("CREATE TABLE labels(scenario TEXT,path TEXT,source_row INTEGER,body TEXT)")
        operational = sqlite3.connect(output / "operational-001.sqlite")
        for scenario in SCENARIOS:
            with zipfile.ZipFile(root / (scenario.split('/')[0] + '.zip')) as z:
                for name in ('record.csv','query.csv'):
                    path = scenario + '/' + name
                    rows = csv_rows(z,path)
                    header = next(rows)
                    if set(header) != LABEL_HEADERS[name]:
                        raise ValueError("unsupported label schema")
                    for line,row in rows:
                        db.execute("INSERT INTO labels VALUES (?,?,?,?)",(scenario,path,line,canonical_json(row)))
                        if name == 'query.csv':
                            queries.append({"scenario":scenario,"row":line,"association":"UNKNOWN; not joined by row order"})
                            continue
                        try:
                            ns = epoch_ns(row['timestamp'],'s')
                            label_dt = datetime.strptime(row['datetime'],'%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone(timedelta(hours=8)))
                            if int(label_dt.timestamp()) * 10**9 != ns:
                                raise ValueError("label datetime/epoch disagreement")
                            ref = SourceRef('OpenRCA-evaluation',digest([scenario,path]),line,row)
                            fault = FaultEvent('fault:'+digest([scenario,line]),ns,row['component'],row['reason'] or None,ref)
                            truth = GroundTruth(scenario+'@'+str(line),row['component'],ns,row['reason'] or None,ref)
                            incident = Incident(truth.incident_id,None,(fault.fault_id,))
                            faults.append({"fault":asdict(fault),"ground_truth":asdict(truth),"incident":asdict(incident)})
                            rid = 'resource:'+digest([scenario,row['component']])
                            presence = operational.execute('SELECT count(*) FROM resources WHERE resource_id=?',(rid,)).fetchone()[0] > 0
                            near = operational.execute('SELECT count(*) FROM observations WHERE resource_id=? AND event_ns BETWEEN ? AND ?',
                                                       (rid,ns-300*10**9,ns+300*10**9)).fetchone()[0]
                            incident_checks.append({"incident_id":truth.incident_id,"root_present_in_sample":presence,
                                "root_telemetry_within_5_minutes_in_sample":near,
                                "label_validity":"NOT_ESTABLISHED; prefix absence is not a missing-label verdict",
                                "deviation_visibility":"NOT_TESTED; no anomaly detector in this task"})
                        except ValueError as exc:
                            issues.append({"scenario":scenario,"row":line,"error":str(exc)})
        operational.close()
    write_new(output / 'ground-truth.json',faults)
    write_new(output / 'incident-coverage.json',incident_checks)
    return {"fault_labels":len(faults),"query_rows":len(queries),"invalid_labels":issues,
            "query_association":"UNKNOWN; original evaluator rules not inferred",
            "incident_root_present":sum(r['root_present_in_sample'] for r in incident_checks),
            "incident_root_near_event":sum(r['root_telemetry_within_5_minutes_in_sample'] > 0 for r in incident_checks)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', required=True)
    p.add_argument('--output',required=True)
    args = p.parse_args()
    repo = Path.cwd()
    config_path = Path(args.config).resolve()
    config = json.loads(config_path.read_text())
    output = Path(args.output)
    output.mkdir(parents=True,exist_ok=False)
    snapshot_before_execution(repo,output,config_path)
    root = repo / config['dataset_root']
    archive_manifest = [{'path':a.name,'bytes':a.stat().st_size,'sha256':file_hash(a)} for a in sorted(root.glob('*.zip'))]
    write_new(output / 'dataset-provenance.json',{'dataset':'OpenRCA','upstream_version':'UNKNOWN','archives':archive_manifest})
    results = []
    for repeat in range(1,config['repetitions']+1):
        print(f'Processing bounded corpus pass {repeat}/{config["repetitions"]}',flush=True)
        results.append(telemetry_pass(root,output,config,repeat))
    evaluation = evaluation_only(root,output)
    first = results[0]
    deterministic = len({r['canonical_sha256'] for r in results}) == 1
    totals = Counter()
    for f in first['files']:
        totals.update(f['counts'])
    gates = {
        'A':{'result':'PARTIAL','reason':'Sample-date validated per-file profiles; whole-file scale and clock semantics unverified.'},
        'B':{'result':'PASS','reason':'Source identities scoped/preserved, explicit kinds including UNKNOWN, unreviewed aliases not applied.'},
        'C':{'result':'PASS','reason':'RUNS_ON derives from workbook cells; CALLS only unique same-trace parents; no causal relations.'},
        'D':{'result':'PASS','reason':'Bounded context, self/missing/ambiguous/unresolved parent states explicit; no invented parents.'},
        'E':{'result':'PARTIAL','reason':'Registry and raw preservation implemented; source metric units/temporality/duration/status remain UNKNOWN.'},
        'F':{'result':'PARTIAL','reason':'Every file sampled and conservation/missingness/duplicates measured; full row counts and incident coverage unverified.'},
        'G':{'result':'PARTIAL','reason':'Evaluation is stored separately and projection excludes raw paths/attributes/log text; complete content and query/edge look-ahead audit pending.'},
        'H':{'result':'PASS' if deterministic else 'FAIL','reason':'Two independent processing passes compared by canonical representation digest.'}}
    if not all(f['row_conservation'] for f in first['files']):
        gates['F'] = {'result':'FAIL','reason':'row conservation failure'}
    if totals['ambiguous'] or totals['unsupported']:
        gates['A'] = {'result':'FAIL','reason':'Ambiguous timestamps or unsupported schemas quarantined; review required.'}
    preflight = json.loads((output / 'preflight.json').read_text())
    historic_unchanged = all(file_hash(repo / name) == h for name,h in preflight['historical_record_hashes'].items())
    summary = {'amendment_id':'E003-AM001','validation_id':output.name,'version':VERSION,
        'gates':gates,'adequacy_passed':all(g['result']=='PASS' for g in gates.values()),
        'decision':'REVISE','review_required':True,'rcaeval_started':False,
        'total_sample_counts':dict(totals),'telemetry_files':len(first['files']),
        'canonical_hashes':[r['canonical_sha256'] for r in results], 'evaluation':evaluation,
        'historical_record_hashes_unchanged':historic_unchanged,
        'source_after_execution_unchanged':all(file_hash(repo / n)==h for n,h in preflight['source_hashes'].items())}
    write_new(output / 'summary.json',summary)
    write_new(output / 'leakage-audit.json',{'result':'PARTIAL','labels_in_operational_database':False,
        'evaluation_storage':'evaluation-only.sqlite; not opened by telemetry_pass',
        'projection_policy':'allowlist; excludes source paths, raw fields, row order, fault/query metadata and log messages',
        'future_policy':'observation event_ns must be in supplied QueryWindow; duration/end UNKNOWN',
        'untested':['benchmark cues within metric/resource/trace names','complete trace-edge query-time filtering',
                    'official evaluator query-to-fault association','complete incident content audit']})
    manifest = {f.relative_to(output).as_posix():{'sha256':file_hash(f),'bytes':f.stat().st_size}
                for f in output.rglob('*') if f.is_file()}
    write_new(output / 'artifact-manifest.json',manifest)
    print(json.dumps({'decision':summary['decision'],'gates':gates,'rows':dict(totals),'rcaeval_started':False},indent=2),flush=True)
    # A successful validation command does not mean the adequacy gate passed.
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
