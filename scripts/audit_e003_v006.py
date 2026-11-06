"""Independent artifact reader for the single V006 recovery pass."""
import argparse
import gzip
import json
from pathlib import Path
import hashlib
from dce_foundation.domain import digest
from dce_foundation.qualification.projection import projection_violations
from dce_foundation.representation_v2.audit import write_new
from validate_e003_am002 import verify_projection


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True)
    run = Path(parser.parse_args().run)
    inventory = json.loads((run/'replay1-inventory.json').read_text())
    preflight = json.loads((run/'preflight.json').read_text())
    labels = json.loads((run/'evaluation-labels.json').read_text())
    config = preflight['configuration']
    expected = {'context:'+digest([l['scenario'],l['fault_ns']-config['incident_before_seconds']*10**9,l['fault_ns']]) for l in labels}
    checks, errors, graph_records = {}, [], []
    windows = inventory['windows']
    checks['windows'] = len(windows)==335 and {w['window_identity'] for w in windows}==expected
    checks['lineage'] = sum(w['origin']=='V004' for w in windows)==164 and sum(w['origin']=='V006' for w in windows)==171
    comparisons = json.loads((run/'replay-comparison.json').read_text())
    checks['comparison'] = comparisons['equal'] and comparisons['passes'][0]==comparisons['passes'][1]
    for ordinal, item in enumerate(windows, 1):
        paths = [Path(item['artifact_path']), run/'cases/replay-002'/item['expected_filename']]
        hashes = []
        for repetition, path in enumerate(paths, 1):
            try:
                with gzip.open(path,'rb') as stream:
                    payload=json.loads(stream.read())
                if (payload['start_ns'],payload['cutoff_ns'])!=(item['start_ns'],item['fault_ns']):
                    raise ValueError('incorrect window bounds')
                if projection_violations(payload):
                    raise ValueError('unsupported projection evidence')
                failures, graph = verify_projection(payload)
                if failures:
                    raise ValueError('independent semantic verification: ' + str(failures[:10]))
                graph_records.append({'handle':item['window_identity'],'repetition':repetition,
                    'nodes':graph.number_of_nodes(),'edges':graph.number_of_edges()})
                hashes.append(digest(payload))
                if repetition==1 and sha(path)!=item['artifact_sha256']:
                    raise ValueError('artifact byte hash mismatch')
                if digest(payload)!=comparisons['passes'][repetition-1][ordinal-1]['canonical_sha256']:
                    raise ValueError('comparison canonical hash mismatch')
            except Exception as error:
                errors.append({'path':str(path),'error':str(error)})
        if hashes!=[item['canonical_sha256']]*2:
            errors.append({'window':item['window_identity'],'error':'independent replay hashes differ'})
        if ordinal%10==0:
            print(json.dumps({'independent_windows_checked':ordinal}),flush=True)
    checks['artifact_integrity_and_equality']=not errors
    replay2 = list((run/'cases/replay-002').glob('*'))
    checks['replay2_coverage']=len(replay2)==335 and {p.name for p in replay2}=={w['expected_filename'] for w in windows}
    checks['reconstructed_only']=len(list((run/'cases/replay-001').glob('*')))==171
    profiles=list((run/'profiles').glob('file-*.json'))
    checks['profile_inheritance']=len(profiles)==162 and all(sha(p)==preflight['parent_fingerprints']['V004'][p.name]['sha256'] for p in profiles)
    unexpected = {p.name for p in run.iterdir()} - {'profiles','cases','logs','preflight.json','source-snapshot.zip',
        'evaluation-labels.json','evaluation-queries.json','evaluation-query-associations.json',
        'evaluation-incident-coverage.json','metric-qualification-registry.json','continuation-provenance.json',
        'context-reference.json','parent-replay1-inventory.json','reconstruction-set.json','replay1-inventory.json','replay-comparison.json'}
    unexpected -= {'verification-amendment.json'}
    checks['no_unexpected_run_files']=not unexpected
    amendment=json.loads((run/'verification-amendment.json').read_text())
    checks['recorded_verifier_version']=sha(Path(__file__))==amendment['auditor_after_sha256']
    write_new(run/'independent-audit.json',{'run_id':'E003-AM002-V006','passed':all(checks.values()),
        'checks':checks,'errors':errors,'independent_graph_records':graph_records,
        'semantic_verifier_source_sha256':sha(Path('scripts/validate_e003_am002.py'))})
    if not all(checks.values()):
        raise SystemExit(1)


if __name__=='__main__':
    main()
