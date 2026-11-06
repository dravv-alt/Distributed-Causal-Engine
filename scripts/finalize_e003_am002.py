"""Finish local E003 evidence after a long census; never starts downstream work."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time


def write_new(path, value):
    with path.open('x', encoding='utf-8') as stream:
        stream.write(value if isinstance(value, str) else json.dumps(value, indent=2, sort_keys=True) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True)
    parser.add_argument('--review-output', required=True)
    parser.add_argument('--wait', action='store_true')
    args = parser.parse_args()
    run, output = Path(args.run), Path(args.review_output)
    started = time.monotonic()
    while not (run / 'artifact-manifest.json').exists():
        if (run / 'failure.json').exists():
            output.mkdir(parents=True, exist_ok=False)
            failure = json.loads((run / 'failure.json').read_text())
            write_new(output / 'decision.md', '# E003-AM002 decision proposal\n\nREVISE / execution incomplete. No PASS is proposed.\n\n```json\n' + json.dumps(failure, indent=2) + '\n```\n\nHistorical records and raw sources are preserved. Stop for review.\n')
            print('Census failed; REVISE proposal recorded.', flush=True)
            return 1
        if not args.wait:
            raise RuntimeError('run is not complete; no report can be finalized')
        if time.monotonic() - started > 86400:
            raise TimeoutError('24-hour monitor limit; qualification remains incomplete')
        time.sleep(15)
    # Wait until the manifest's exclusive writer has closed and JSON is complete.
    for attempt in range(20):
        try:
            json.loads((run / 'artifact-manifest.json').read_text())
            break
        except json.JSONDecodeError:
            time.sleep(1)
    else:
        raise RuntimeError('artifact manifest is not complete JSON')
    output.mkdir(parents=True, exist_ok=False)
    result = subprocess.run([sys.executable, 'scripts/validate_e003_am002.py', '--run', str(run),
                             '--output', str(output / 'independent-audit.json')], capture_output=True, text=True)
    write_new(output / 'independent-audit-stdout.log', result.stdout)
    write_new(output / 'independent-audit-stderr.log', result.stderr)
    if result.returncode:
        write_new(output / 'decision.md', '# E003-AM002 decision proposal\n\nREVISE / independent validation did not complete. See audit logs. No downstream experiment is authorized.\n')
        return result.returncode
    audit = json.loads((output / 'independent-audit.json').read_text())
    summary = json.loads((run / 'summary.json').read_text())
    coverage = json.loads((run / 'evaluation-incident-coverage.json').read_text())
    profiles = [json.loads(p.read_text()) for p in sorted(run.glob('file-*.json'))]
    groups = defaultdict(Counter)
    per_file = []
    dispositions = Counter()
    for profile in profiles:
        groups[profile['scenario']]['files'] += 1
        groups[profile['scenario']]['rows'] += profile['counts']['rows_seen']
        dispositions.update(profile['selection_counts'])
        selected_counts = {k: v for k, v in profile['selection_counts'].items() if k != 'shape_errors'}
        per_file.append({'path': profile['path'], 'rows': profile['counts']['rows_seen'],
                         'timestamp_status': profile['decision'], 'timestamp_scale': profile['selected_scale'],
                         'selected_counts': profile['selection_counts'],
                         'coverage_loss_fraction_selected': sum(v for k, v in selected_counts.items() if k != 'mapped') / max(1, sum(selected_counts.values())),
                         'whole_file_shape_error_rows': profile['selection_counts'].get('shape_errors', 0),
                         'whole_file_shape_error_fraction': profile['selection_counts'].get('shape_errors', 0) / max(1, profile['counts']['rows_seen']),
                         'timestamp_counts': profile['counts'], 'crc_eof_verified': profile['crc_eof_verified']})
    for case in coverage:
        counts = groups[case['scenario']]
        counts['incidents'] += 1
        counts['root_observed'] += bool(case['root_observation_found'])
        counts['root_before_or_at'] += bool(case['before_only_task_eligible'])
        counts['root_trace'] += bool(case['root_trace_found'])
        counts['case_query_link_unknown'] += case['query_association'] == 'UNKNOWN'
        counts['no_mapped_telemetry'] += case['coverage_status'] == 'NO_MAPPED_TELEMETRY'
    metrics = json.loads((run / 'metric-qualification-registry.json').read_text())
    accepted = summary['representation_passed'] and audit['passed']
    outcome = 'PASS for annotation-window representation; RESTRICTED evaluation readiness' if accepted else 'REVISE'
    tables = ['| Scenario | Files | Source rows | Incidents | Root observed ±5min | Root before/at cutoff | Root trace |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for scenario, counts in sorted(groups.items()):
        tables.append('| ' + scenario + ' | ' + ' | '.join(str(counts[k]) for k in ('files', 'rows', 'incidents', 'root_observed', 'root_before_or_at', 'root_trace')) + ' |')
    gate_table = '\n'.join('| ' + gate + ' | ' + status + ' |' for gate, status in summary['gates'].items())
    facts = {'created_at_utc': datetime.now(timezone.utc).isoformat(), 'outcome_proposal': outcome,
             'human_review_required': True, 'summary': summary, 'cross_system': dict(groups),
             'file_dispositions': per_file, 'selected_dispositions': dict(dispositions),
             'metric_registry_entries': len(metrics), 'metric_statuses': dict(Counter(m['status'] for m in metrics)),
             'independent_audit_passed': audit['passed'], 'root_nodes_before_cutoff': audit['root_node_cases_before_cutoff'],
             'automatic_downstream_execution': False, 'raw_deleted': False}
    write_new(output / 'results.json', facts)
    report = f'''# E003-AM002 qualification report

## Plain-language result

Proposed outcome: **{outcome}**. Human review is required. This checks whether the data representation is trustworthy, not whether DCE can diagnose a fault.

The census completed {summary['files']} telemetry files and {summary['total_source_rows']:,} source rows. All {summary['labels']} annotations have incident-centered coverage records. Independent verification checked {audit['cases_verified']} saved case/repetition outputs. Historical records unchanged: {summary['historical_records_unchanged']}; independent integrity check passed: {audit['passed']}.

## What OpenRCA contains

Three system archives, four scenarios, long and wide metric tables, distributed span tables, Bank/Market logs, fault annotations, natural-language evaluation queries, and Telecom workbook resource relations. Schemas differ by system; timestamps require per-file evidence. The original corpus remains intact. The detailed schemas and v2 mappings remain in AM001; AM002 adds full-file evidence rather than overwriting that report.

{chr(10).join(tables)}

## What is represented

Exact selected source strings and row identity, nanosecond event-time interpretation, resources, metrics with explicit UNKNOWN semantics, spans and explicit parent-reference states, evidence-backed temporal CALLS edges, and evaluator-owned labels/query associations. Uncertain service aliases and workbook edge validity are not invented.

## Gates

| Gate | Run result |
| --- | --- |
{gate_table}

The run's B/D flags rely on the established v2 foundation; the separate independent audit reconstructs identity tokens, typed NetworkX graphs and parent-state/edge conservation from actual saved outputs. Use both records, not the summary alone.

## Information loss and assumptions

The context store retains only incident-window source rows, not the complete corpus. Rows outside those windows are censused and hashed, not copied. Inference intentionally excludes raw names, paths, free log text, status/type/operation text, labels and scoring points. Raw selected fields remain in the audit store. UNKNOWN duration units do not create span end times. Workbook relations with UNKNOWN temporal validity are excluded from time-qualified inference. UTC+08 source-local dates, the fixed one-hour profile allowance and the fixed ±5-minute audit window are declared assumptions.

## Coverage, inconsistencies and failures

{summary['root_observed_cases']} of {summary['labels']} annotations have exact-root telemetry within the audit window; {summary['before_only_root_observed_cases']} have it before/at the inference cutoff. Missing root evidence is reported, not silently dropped. Presence alone does not establish label validity or visible deviation. Rejected selected rows and timestamp boundary/invalid counts appear per file in results.json, with denominators; they are not silently loaded as valid evidence.

There are {summary['unknown_metric_entries']} UNKNOWN metric-registry entries. Unknown semantics are acceptable only for representation, not unit-dependent feature computation. Query associations: {summary['qualified_query_associations']}/{summary['queries']} qualified; two remain UNKNOWN as documented in query-association-limitations.md. The reason-only repeated-fault query and cross-midnight parser limitation restrict unrestricted official scoring. The source schema differences, ordering reversals, boundary timestamps and unresolved parent states are retained in the raw profiles and replay summaries.

V001 was intentionally interrupted for a lossless physical-storage redesign. Eleven EOF-verified profiles were inherited into V002 with hashes and conserved selection counts. The interrupted file was rescanned. This is one complete census assembled from verified file checkpoints, not two complete raw scans.

## Determinism and resources

Two independent projected replays equal: {json.loads((run / 'replay-comparison.json').read_text())['equal']}. Per-case canonical/edge hashes and saved payloads are independently verified. This is local artifact replay repeatability, not a claim about cross-platform or learned-model reproducibility. V002 elapsed seconds: {summary['elapsed_seconds']:.2f}; peak process memory bytes: {summary['peak_memory_bytes']}; context database bytes: {summary['context_store_bytes']}. The eleven inherited profile timings are separate and V001's interrupted work is not included in this V002 elapsed figure.

## What must happen next

Review this report and independent-audit.json. If accepted, annotation-window representation is a supported substrate for a separately specified next experiment. Before unrestricted official-query scoring, qualify repeated-element association and cross-date query-window parsing. Before metric transformations, qualify needed units/temporality; before service-level reasoning, qualify any required aliases/topology. No diagnosis, anomaly detection, RCA accuracy comparison, RCAEval integration or deletion audit was executed here. Raw-data deletion remains unauthorized and requires a separate preserve/restore/reproducibility audit.
'''
    write_new(output / 'report.md', report)
    write_new(output / 'decision.md', f'''# E003-AM002 decision proposal

**{outcome}**.

This is a proposal, not human approval and not a retroactive change to E003-R001 or AM001. Existing register numbering is unchanged. Mechanical gate results and independent validation are in report.md/results.json/independent-audit.json.

Do not advance automatically. Annotation-window representation, official-query scoring readiness, root observability and diagnostic accuracy are different claims. Two query associations remain UNKNOWN; required evaluator revisions are recorded in query-association-limitations.md. No RCAEval or reasoning work starts, and no raw data is deleted.
''')
    print(json.dumps({'outcome_proposal': outcome, 'review_output': str(output), 'human_review_required': True}, indent=2), flush=True)
    return 0 if accepted else 1


if __name__ == '__main__':
    raise SystemExit(main())
