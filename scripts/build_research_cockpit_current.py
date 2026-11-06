"""Presentation-only current snapshot; historical adapter and experiment records stay intact."""
import json
from datetime import datetime, timezone
from scripts.build_research_cockpit_data import ROOT, OUT, artifact, build as old_build, read_json


def build():
    data = old_build()
    data.update(schema_version='dce.research-cockpit.v2', generated_at=datetime.now(timezone.utc).isoformat())
    data['current_stage'] = {'title':'First real-data ranking test complete','status':'REVIEW','plain':'Replay works consistently. The graph ranking scored below the simpler observation-count method. Reliable diagnosis and automatic fixing are not established.'}
    data['next_action'] = 'Review E004’s proposed REVISE decision. No successor experiment or automatic fixing has been approved.'
    e1,e2,e3 = data['experiments']
    e1.update(status='ACCEPTED',execution_status='Reproduction completed',review_status='User accepted R001 REVISE',blocking='Review accepted; E002 subsequently executed.',waiting='Retain R0 as a baseline, not proof of hybrid superiority.')
    e1['artifacts'].append(artifact('Comparison and hashes','experiments/E001/results/E001-R001/artifact-manifest.json'))
    p2='experiments/E002/results/E002-R002/'
    s2,v2=read_json(p2+'summary.json'),read_json(p2+'validation.json')
    e2.update(run_id='E002-R002',status='REVIEW',execution_status=v2['outcome'],review_status='R001 accepted; R002 proposal pending review',
        result='Three repeats agree. Clean-environment qualification passed. The timing change still gave no ranking improvement.',
        what_we_did='Reran the frozen synthetic timing experiment in a qualified environment: three repeats and five fixed held-out seeds, comparing mixed, same-source and disabled timing.',
        meaning='The tied result survived the environment fix. The old dependency warning does not explain away the lack of improvement.',
        blocking='The environment issue is fixed for R002. Its proposal remains pending; E003 infrastructure was accepted separately.',
        waiting='Review R002’s REVISE proposal separately from the accepted R001.',
        facts=[f"Top-1 difference: {s2['paired_top1_same_source_minus_mixed']['mean']:.3f} across {s2['paired_top1_same_source_minus_mixed']['n_events']} events.",
               'Mixed timing used 306 cross-source pairs; same-source timing used zero.',
               'Preflight and postflight qualified; 49 tests passed. Raw results byte-identical to R001.',
               'Downloaded hash-pinned clean-room reconstruction was not established.'],
        gates=[{'name':key.replace('_',' '),'status':'PASS' if value else 'FAIL'} for key,value in v2['gates'].items()],
        artifacts=[artifact(label,p2+file) for label,file in [('Results','summary.json'),('Environment / tests','validation.json'),('Decision proposal','decision-proposal.md'),('R001 comparison','comparison-r001-r002.md')]],
        technical={'summary':s2,'validation':v2},history=['R001: accepted REVISE; environment qualification failed.','R002: qualified environment; unchanged performance; proposal pending.'])
    p3='experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V006/'
    s3=read_json(p3+'summary.json')
    approval='docs/governance/amendments/2026-10-06-E003-V006-acceptance-and-E004-scope.md'
    if 'Review status: APPROVED' not in (ROOT/approval).read_text(encoding='utf-8'):
        raise ValueError('E003 infrastructure approval missing')
    e3.update(run_id=s3['run_id'],status='ACCEPTED',execution_status=s3['recovery_status'],review_status='Accepted only as representation/replay infrastructure',
        question='Can DCE preserve and replay real OpenRCA telemetry consistently?',
        result=f"{s3['inherited_profiles']}/162 profiles; both replays verified {s3['replay1']['verified']}/335 windows. Independent audit passed.",
        what_we_did='Recovered saved profiles, reused 164 valid windows, reconstructed 171, then replayed all 335 again and compared hashes.',
        meaning='The representation/replay foundation is accepted. Preserving measurements is not the same as understanding them or finding faults.',
        not_established='It does not prove full scientific adequacy, diagnosis accuracy, causal relationships or production readiness. Conditions B and D were inherited, not retested.',
        blocking='No for the approved restricted E004 baseline. Unknown metric meanings and coverage still restrict stronger claims.',
        waiting='Infrastructure accepted; scientific disposition remains REVISE. E004 has used this foundation.',
        facts=[f"{s3['unknown_metric_entries']:,} metric meanings remain UNKNOWN.",f"Before-only root coverage: {s3['before_only_root_observed_cases']}/335; coverage is not accuracy.",
               'Supplied fault times define retrospective windows, not online detection.',
               'Launcher status 1 with environment warning; completed artifacts independently verified.'],
        gates=[{'name':'Condition '+k,'status':'PASS' if v=='PASS' else 'NOT RETESTED'} for k,v in s3['gates'].items()],
        artifacts=[artifact(label,p3+file) for label,file in [('Summary','summary.json'),('Audit','independent-audit.json'),('Results','results.json'),('Scientific decision','decision.md'),('Hashes','artifact-manifest.json')]]+[artifact('Limited acceptance',approval)],technical=s3,
        history=['R001: bounded audit; adequacy not established.','V002: 77/162 partial checkpoint, preserved.','V004: interrupted checkpoint, preserved.','V005: failed engineering attempt, preserved.','V006: completed; accepted for representation/replay only.'])
    p4='experiments/E004_symbolic_rca_baseline/results/E004-R001/'
    s4,r4=read_json(p4+'summary.json'),read_json(p4+'results.json')
    labels={'symbolic_topology_v1':'Graph: shared dependencies','activity_reference_v1':'Simple: observation counts','graph_disabled_uniform_v1':'Reference: uniform chance'}
    data['experiments'].append(dict(experiment_id='E004',run_id=s4['run_id'],status='REVIEW',decision='REVISE',execution_status=s4['status'],review_status='Decision proposal pending human review',
        question='Does knowing who calls whom help locate the faulty component?',
        what_we_did='Ranked the same 335 windows by shared dependencies, observation counts and uniform chance. Recomputed each ranking twice, then independently audited it.',
        result='The graph method scored above chance, but below the simpler observation-count ranking.',
        meaning='This heuristic contains descriptive localization signal. Dependency structure alone did not give reliable localization in this benchmark.',
        not_established='No statistically established superiority, causality, operational RCA, online detection, hybrid advantage or safe remediation. Not official OpenRCA scoring.',
        blocking='Human review required before any successor. No successor started.',waiting='Review REVISE / structural-prior-only. Technical PASS does not mean diagnostic success.',
        facts=[f"All {s4['cases']} windows retained; {s4['repeatability_cases']} repeat computations agreed; audit passed.",f"Root present: {s4['overall']['root_present']}/335; all {s4['overall']['root_absent']} absent-root cases remain in the denominator.",
               'No qualified symptom detector: a shared dependency is not necessarily broken.','Fault time was supplied. Overlapping windows prevent significance claims from descriptive intervals.'],
        gates=[{'name':'Execution / audit','status':s4['technical_gate']},{'name':'Superiority','status':'NOT ESTABLISHED'}],
        comparison=[dict(method_id=k,label=v,**s4['overall']['methods'][k]) for k,v in labels.items()],
        per_system=[dict(system=k,**v) for k,v in r4['per_system'].items() if k!='ALL'],
        artifacts=[artifact(label,p4+file) for label,file in [('Plain decision','decision.md'),('Summary','summary.json'),('Per-system results','results.json'),('Audit','independent-audit.json'),('Prediction seal','prediction-seal.json'),('Hashes','artifact-manifest.json')]],technical=s4))
    return data


if __name__=='__main__':
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(build(),indent=2)+'\n',encoding='utf-8')
    print(OUT.relative_to(ROOT))
