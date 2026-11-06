"""Read retained metadata only; no detector, raw scan, registration or experiment."""
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V006 = ROOT / 'experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V006'
OUT = ROOT / 'docs/research-design/2026-10-08-symptom-evidence'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    targets = [OUT/name for name in ['metric-eligibility-inventory.csv', 'inspection-summary.json', 'inspection-source-hashes.json']]
    if any(p.exists() for p in targets):
        raise FileExistsError('Dated inspection outputs already exist; refusing to overwrite.')
    manifest_path = V006 / 'artifact-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    profiles_paths = sorted((V006/'profiles').glob('*.json'))
    result_paths = [V006/name for name in ['metric-qualification-registry.json', 'summary.json', 'evaluation-incident-coverage.json', 'context-reference.json']]
    sources = [manifest_path, *profiles_paths, *result_paths]
    sources += [ROOT/p for p in ['AGENTS.md', 'EXPERIMENTAL_PROTOCOL.md', 'PROJECT_STATE.md', 'PROJECT_STATE_2026-10-06_E004.md', 'EXPERIMENT_INDEX.md', 'EXPERIMENT_INDEX_AMENDMENT_2026-10-06_E004.md', 'docs/governance/project-state.json', 'docs/governance/EXECUTION_ROADMAP.md', 'docs/governance/execution-plan.json', 'docs/governance/registrations/E004.json', 'docs/governance/amendments/2026-10-06-E003-V006-acceptance-and-E004-scope.md', 'DCE_PROGRESS_REPORT_2026-10-08.md', 'src/dce_foundation/qualification/semantics.py', 'src/dce_foundation/qualification/projection.py', 'src/dce_foundation/qualification/scan.py', 'src/dce_foundation/qualification/time_profile.py', 'experiments/E003_domain_model_adequacy/qualification/2026-10-04/protocol.md', 'experiments/E003_domain_model_adequacy/qualification/2026-10-04/representation-boundaries.md', 'experiments/E004_symbolic_rca_baseline/protocol.md', 'experiments/E004_symbolic_rca_baseline/results/E004-R001/summary.json', 'experiments/E004_symbolic_rca_baseline/results/E004-R001/decision.md']]
    before = {p.relative_to(ROOT).as_posix():sha(p) for p in sources}
    for p in [*profiles_paths, *result_paths]:
        relative = p.relative_to(V006).as_posix()
        expected = manifest['files'].get(relative)
        if expected is None or sha(p) != expected['sha256'] or p.stat().st_size != expected['bytes']:
            raise ValueError('Frozen artifact mismatch: '+relative)
    registry = json.loads(result_paths[0].read_text(encoding='utf-8'))
    summary = json.loads(result_paths[1].read_text(encoding='utf-8'))
    coverage = json.loads(result_paths[2].read_text(encoding='utf-8'))
    profiles = [json.loads(p.read_text(encoding='utf-8')) for p in profiles_paths]
    profile_by_source = {(p['scenario'],p['path']):p for p in profiles}
    if len(profile_by_source) != len(profiles):
        raise ValueError('Duplicate source profile identity')
    if len(registry) != summary['unknown_metric_entries'] or len(profiles) != summary['inherited_profiles']:
        raise ValueError('Summary/inventory accounting conflict')
    keys = [(e['scenario'],e['source'],e['metric_name']) for e in registry]
    if len(set(keys)) != len(keys):
        raise ValueError('Duplicate registry key')
    # These guards describe this retained registry. A later qualified record
    # must be reviewed by a different dated inspection, never silently promoted.
    for e in registry:
        if e['status'] != 'UNKNOWN' or e['evidence_source'] is not None or e['confidence'] != 0:
            raise ValueError('Registry state differs from this inspection scope')
        if any(e[k] != 'UNKNOWN' for k in ['unit','kind','temporality','aggregation']):
            raise ValueError('Unsupported semantic assertion in UNKNOWN record')
        p = profile_by_source[(e['scenario'],e['source'])]
        if p['metric_counts'].get(e['metric_name']) != e['source_observations']:
            raise ValueError('Registry/profile metric-count mismatch')
    if sum(p['counts']['rows_seen'] for p in profiles) != summary['total_source_rows']:
        raise ValueError('Inherited source-row total conflict')
    if len(coverage) != summary['replay1']['verified']:
        raise ValueError('Coverage/population conflict')
    counts = {
        'registry_entries':len(registry),
        'distinct_scenario_metric_name_pairs':len({(e['scenario'],e['metric_name']) for e in registry}),
        'registry_status_counts':dict(Counter(e['status'] for e in registry)),
        'registry_entries_by_scenario':dict(Counter(e['scenario'] for e in registry)),
        'documented_qualified_registry_entries':sum(e['status']=='QUALIFIED' for e in registry),
        'inherited_source_profiles':len(profiles),
        'profile_decision_counts':dict(Counter(p['decision'] for p in profiles)),
        'profiles_by_modality':dict(Counter('span' if p['path'].endswith('trace_span.csv') else 'log' if '/log/' in p['path'] else 'metric' for p in profiles)),
        'profile_scales_by_scenario':{s:dict(Counter(p['selected_scale'] for p in profiles if p['scenario']==s)) for s in sorted({p['scenario'] for p in profiles})},
        'inherited_source_rows':sum(p['counts']['rows_seen'] for p in profiles),
        'all_profile_row_conservation':all(p['row_conservation'] for p in profiles),
        'all_profile_crc_eof_flags':all(p['crc_eof_verified'] for p in profiles),
        'coverage_cases':len(coverage),
        'cases_by_scenario':dict(Counter(c['scenario'] for c in coverage)),
        'root_before_only_available':sum(c['before_only_task_eligible'] for c in coverage),
        'root_before_only_unavailable':sum(not c['before_only_task_eligible'] for c in coverage),
    }
    rows = []
    for e in registry:
        p = profile_by_source[(e['scenario'],e['source'])]
        rows.append({
            'scenario':e['scenario'], 'metric_name':e['metric_name'], 'source':e['source'],
            'source_observations_inherited':e['source_observations'],
            'source_name_identity':'KNOWN_EXACT_SOURCE_STRING', 'physical_metric_identity':'UNKNOWN',
            'component_service_mapping':'UNKNOWN', 'source_provenance':'KNOWN_RETAINED_PROFILE',
            'timestamp_scale_inherited':p['selected_scale'], 'timestamp_profile_status_inherited':p['decision'],
            'unit':e['unit'], 'kind':e['kind'], 'semantic_meaning':'UNKNOWN',
            'temporality':e['temporality'], 'aggregation':e['aggregation'],
            'sampling_behavior':'UNKNOWN', 'reset_behavior':'UNKNOWN', 'missingness_semantics':'UNKNOWN',
            'registry_status':e['status'], 'symptom_qualification_eligibility':'NOT_ESTABLISHED',
            'reason':'No qualified semantics or defensible healthy-reference policy established',
        })
    OUT.mkdir(parents=True,exist_ok=True)
    with targets[0].open('x',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    with targets[0].open(encoding='utf-8',newline='') as f:
        written=list(csv.DictReader(f))
    if len(written)!=len(registry) or [(r['scenario'],r['source'],r['metric_name']) for r in written]!=keys:
        raise ValueError('Output row accounting/identity failed')
    if any(sha(ROOT/p)!=h for p,h in before.items()):
        raise ValueError('Existing source changed during inspection')
    assessment={
        'schema_version':'dce.symptom-evidence-inspection.v1',
        'inspection_time_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Retained metadata/source inspection; no raw scan, database query, projection replay or detector',
        'assessment':'NOT SUPPORTED',
        'assessment_scope':'Current evidence does not support a scientifically valid symptom-detection qualification execution',
        'experiment_registered':False, 'experiment_executed':False, 'review_required':True,
        'counts':counts,
        'healthy_reference':'NOT ESTABLISHED; retained windows are fault-conditioned, not certified healthy controls',
        'holdout':'NOT ESTABLISHED; all 335 E004 cases have been inspected',
        'interpretation':'Zero documented QUALIFIED registry entries does not prove the raw telemetry contains no useful signal',
        'next_action':'Review an evidence-acquisition scope for metric semantics and independently documented normal controls',
        'checks':{'registry_profile_count_mismatches':0,'csv_identity_accounting':'PASS','source_preservation':'PASS','frozen_metadata_and_profile_hashes':'PASS'},
    }
    with targets[1].open('x',encoding='utf-8') as f:
        json.dump(assessment,f,indent=2,ensure_ascii=False)
    with targets[2].open('x',encoding='utf-8') as f:
        json.dump({'input_hashes':before,'output_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in targets[:2]},'limitations':'Hashes cover cited metadata and sources, not a fresh raw-corpus scan or all replay payloads'},f,indent=2)
    print(json.dumps({'assessment':assessment['assessment'],'counts':counts,'checked_input_files':len(before),'output_csv_rows':len(written)},ensure_ascii=False))


if __name__=='__main__':
    main()
