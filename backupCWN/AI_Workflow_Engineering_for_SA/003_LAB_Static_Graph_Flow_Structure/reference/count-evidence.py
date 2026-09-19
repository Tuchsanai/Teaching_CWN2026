"""Recompute timings, usage and artifact checks from retained run evidence."""
import csv
import gzip
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

REF = Path(__file__).resolve().parent
LAB = REF.parent
STEPS = {
    'customer': 'step-01-fanout/customer',
    'kitchen-front': 'step-01-fanout/kitchen-front',
    'manager': 'step-01-fanout/manager',
    'state-machine': 'step-02-state-machine',
    'structure': 'step-03-structure',
    'merge': 'step-04-merge',
}


def events(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def original_bytes(path):
    archive = Path(str(path) + '.raw.gz')
    return gzip.decompress(archive.read_bytes()) if archive.exists() else path.read_bytes()


def archived_source(path):
    if path == 'input/fr-nfr-input.md':
        return REF / 'step-00-input/fr-nfr-input.md'
    if path in ('work/input-source.md', 'work/input-audit.md'):
        return REF / 'step-00-input' / Path(path).name
    match = re.fullmatch(r'work/flow-(.+)\.(md|json)', path)
    if match and match[1] in STEPS:
        return REF / STEPS[match[1]] / Path(path).name
    if path == 'work/state-machine.md':
        return REF / 'step-02-state-machine/state-machine.md'
    if path == 'work/structure.md':
        return REF / 'step-03-structure/structure.md'
    if path.startswith('input/') or path.startswith('../docs/'):
        return LAB / path
    raise ValueError(f'Unmapped source: {path}')


def main():
    from jsonschema import Draft202012Validator
    schema = json.loads((LAB / 'input/node-output.schema.json').read_text())
    fr = (REF / 'step-00-input/fr-nfr-input.md').read_text()
    scope = {f'US-{n:02}' for n in (1,2,3,4,5,6,7,8,10,11,12,13,15,16,19,20,25,26)}
    checks, nodes, rows, attempts = {}, {}, [], []
    for node, step in STEPS.items():
        directory = REF / step
        meta = json.loads((directory / 'meta.json').read_text())
        ev = events(directory / 'log.jsonl')
        completed = [e for e in ev if e.get('type') == 'turn.completed']
        failed = [e for e in ev if e.get('type') == 'turn.failed']
        usage = completed[-1]['usage'] if completed else None
        assert usage == meta['usage'], node
        duration = Decimal(meta['end_epoch']) - Decimal(meta['start_epoch'])
        nodes[node] = {**meta, 'duration_s': float(duration), 'log': f'{step}/log.jsonl'}
        rows.append({'node': node, 'duration_s': str(duration),
                     'input_tokens': usage['input_tokens'] if usage else 'ไม่มีข้อมูล',
                     'output_tokens': usage['output_tokens'] if usage else 'ไม่มีข้อมูล'})
        for path in sorted(directory.glob('meta*.json')):
            attempt = json.loads(path.read_text())
            log = path.with_name(path.name.replace('meta', 'log').replace('.json', '.jsonl'))
            cev = [e for e in events(log) if e.get('type') == 'turn.completed']
            attempts.append({'node': node, 'attempt': attempt['attempt'],
                             'duration_s': attempt['duration_s'],
                             'duration_scope': attempt.get('duration_scope', 'one invocation'),
                             'usage': cev[-1]['usage'] if cev else None,
                             'log': str(log.relative_to(REF))})
        data = json.loads((directory / f'flow-{node}.json').read_text())
        md = (directory / f'flow-{node}.md').read_text()
        errors = [e.message for e in Draft202012Validator(schema).iter_errors(data)]
        coverage = {u for flow in data['flows'] for u in flow['us_refs']}
        evidence_ok = all(e['quote'] in fr and e['fr_id'] in fr
                          for flow in data['flows'] for e in flow['evidence'])
        flow_md_ok = all(f['flow_id'] in md for f in data['flows'])
        fr_coverage_ok = all(set(f['fr_refs']) <= {e['fr_id'] for e in f['evidence']} for f in data['flows'])
        conflicts = data['conflicts_found']
        source_hashes_ok = all(hashlib.sha256(original_bytes(archived_source(s['path']))).hexdigest() == s['sha256']
                               for s in data['sources'])
        resolved_evidence_ok = all(c['fr_refs'] and c['evidence'] and all(q in fr for q in c['evidence'])
                                   for c in conflicts if c['status'] == 'resolved')
        checks[node] = {'execution_completed': bool(completed) and not failed and meta['exit_code'] == 0,
                        'schema_errors': errors, 'flow_count': len(data['flows']),
                        'markdown_lines': len(md.splitlines()), 'us_coverage': sorted(coverage),
                        'scope_ok': coverage <= scope,
                        'archived_source_hashes_ok': source_hashes_ok,
                        'verbatim_fr_evidence_ok': evidence_ok,
                        'flow_ids_in_markdown': flow_md_ok,
                        'fr_refs_have_evidence': fr_coverage_ok,
                        'resolved_conflicts_have_verbatim_evidence': bool(resolved_evidence_ok),
                        'conflicts_resolved': sum(c['status'] == 'resolved' for c in conflicts),
                        'conflicts_unresolved': sum(c['status'] == 'unresolved' for c in conflicts)}
    initial = json.loads((REF / 'parallel-meta.json').read_text())
    retry = json.loads((REF / 'parallel-retry-meta.json').read_text())
    roots = [nodes[n] for n in ('customer', 'kitchen-front', 'manager')]
    end = max(Decimal(initial['end_epoch']), Decimal(retry['end_epoch']), *(Decimal(n['end_epoch']) for n in roots))
    overlap = min(Decimal(n['end_epoch']) for n in roots) - max(Decimal(n['start_epoch']) for n in roots)
    timing = {'nodes': nodes,
              'wall_parallel_seconds': float(end - Decimal(initial['start_epoch'])),
              'wall_workflow_seconds': float(Decimal(nodes['merge']['end_epoch']) - Decimal(initial['start_epoch'])),
              'sum_node_seconds': sum(n['duration_s'] for n in nodes.values()),
              'sum_fanout_node_seconds': sum(n['duration_s'] for n in roots),
              'successful_fanout_overlap_seconds': float(overlap),
              'all_attempts_sum_node_seconds': sum(a['duration_s'] for a in attempts),
              'all_attempts_fanout_sum_seconds': sum(a['duration_s'] for a in attempts if a['node'] in ('customer','kitchen-front','manager')),
              'attempts': attempts,
              'actual_cli_invocations': len(attempts) + 1,
              'missing_stdout_usage': [{'node': 'manager', 'attempt': 1, 'input_tokens': None, 'output_tokens': None,
                                        'reason': 'Original stdout accidentally overwritten; original session retained, no turn.completed stdout usage available.'}],
              'parallel_timing_note': 'From first background launch through all root completions, including blocked attempts, unintended manager invocation and retries. Manager attempt-2 duration encloses attempts 1 and 2. sum_node_seconds covers only six retained successful executions.'}
    assert overlap > 0, 'Successful role executions did not overlap'
    (REF / 'timing.json').write_text(json.dumps(timing, ensure_ascii=False, indent=2) + '\n')
    with (REF / 'metrics.csv').open('w') as out:
        writer = csv.DictWriter(out, fieldnames=['node','duration_s','input_tokens','output_tokens'])
        writer.writeheader()
        writer.writerows(rows)
    original = json.loads((REF / 'step-00-input/original-input-prompt-hashes.json').read_text())
    checks['original_files_unchanged'] = all(hashlib.sha256((LAB / p).read_bytes()).hexdigest() == h for p,h in original.items())
    (REF / 'check-report.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'nodes': len(nodes), 'attempts': len(attempts), 'parallel_seconds': timing['wall_parallel_seconds'],
                      'successful_overlap_seconds': float(overlap), 'checks': checks}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
