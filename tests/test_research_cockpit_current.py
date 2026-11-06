import hashlib
import json
from scripts.build_research_cockpit_current import ROOT, build


def test_runs_and_review_boundaries():
    d=build(); e={x['experiment_id']:x for x in d['experiments']}
    assert list(e)==['E001','E002','E003','E004']
    assert e['E002']['run_id']=='E002-R002'
    assert e['E002']['technical']['validation']['environment']['postflight_qualified']
    assert e['E003']['technical']['replay1']['verified']==335
    assert e['E003']['technical']['gates']['B'].startswith('NOT RETESTED')
    assert '77/162 partial' in ' '.join(e['E003']['history'])
    assert e['E004']['status']=='REVIEW'
    assert not e['E004']['technical']['superiority_established']
    json.dumps(d)


def test_primary_scoring_and_all_cases():
    e=build()['experiments'][3]; r={x['method_id']:x for x in e['comparison']}
    g=r['symbolic_topology_v1']['top1_tie_aware']
    assert r['graph_disabled_uniform_v1']['top1_tie_aware']<g<r['activity_reference_v1']['top1_tie_aware']
    assert round(g*100,2)==3.08
    assert sum(s['cases'] for s in e['per_system'])==335
    assert sum(s['root_present'] for s in e['per_system'])==284


def test_evidence_paths_and_hashes():
    for e in build()['experiments']:
        for a in e['artifacts']:
            p=ROOT/a['path']
            assert p.is_file()
            assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']


def test_http_page_snapshot_and_original_evidence():
    from functools import partial
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread
    from urllib.request import urlopen
    handler=partial(SimpleHTTPRequestHandler,directory=str(ROOT))
    server=ThreadingHTTPServer(('127.0.0.1',0),handler)
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f'http://127.0.0.1:{server.server_port}/'
    try:
        with urlopen(base+'frontend/research-cockpit/') as response:
            assert b'current.js' in response.read()
        for path in ['frontend/research-cockpit/current.js','frontend/research-cockpit/results.css','frontend/research-cockpit/data/experiments.json']:
            with urlopen(base+path) as response:
                assert response.status==200
        for e in build()['experiments']:
            for a in e['artifacts']:
                with urlopen(base+a['path']) as response:
                    assert hashlib.sha256(response.read()).hexdigest()==a['sha256']
    finally:
        server.shutdown();server.server_close();thread.join(timeout=2)
