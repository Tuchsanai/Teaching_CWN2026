"""Read-only validation for LAB003. Human review remains a separate decision."""
import argparse
import hashlib
import json
from pathlib import Path
import re

LAB = Path(__file__).resolve().parents[1]
SCOPE = {f'US-{i:02}' for i in (1,2,3,4,5,6,7,8,10,11,12,13,15,16,19,20,25,26)}
ROLES = {
    'customer': {f'US-{i:02}' for i in range(1,9)},
    'kitchen-front': {f'US-{i:02}' for i in (10,11,12,13,15,16)},
    'manager': {f'US-{i:02}' for i in (19,20,25,26)},
}

def read(p):
    q = LAB / p
    assert q.is_file() and q.stat().st_size, f'Missing/empty: {p}'
    return q.read_text(encoding='utf-8')

def digest(p):
    return hashlib.sha256((LAB / p).read_bytes()).hexdigest()

def graph_check():
    g = json.loads(read('input/graph.json'))
    nodes = {n['id']: n for n in g['nodes']}
    assert len(nodes) == len(g['nodes']) == 6, 'Duplicate/missing node'
    assert {n['id'] for n in nodes.values() if not n['depends_on']} == set(ROLES)
    assert set(nodes['state-machine']['depends_on']) == set(ROLES)
    assert set(nodes['structure']['depends_on']) == set(ROLES)
    assert set(nodes['merge']['depends_on']) == set(nodes) - {'merge'}
    expected = {(d, n['id']) for n in nodes.values() for d in n['depends_on']}
    actual = [(e['from'], e['to']) for e in g['edges']]
    assert len(actual) == len(set(actual)) and set(actual) == expected, 'Edge/dependency mismatch'
    order = []
    def visit(i, stack=()):
        assert i in nodes and i not in stack, f'Cycle/unknown dependency: {i}'
        if i in order:
            return
        n = nodes[i]
        assert all(k in n for k in ('id','role','prompt','inputs','outputs','depends_on'))
        read(n['prompt'])
        for dep in n['depends_on']:
            visit(dep, stack + (i,))
        order.append(i)
    for i in nodes:
        visit(i)
    all_outputs = [p for n in nodes.values() for p in n['outputs']]
    assert len(all_outputs) == len(set(all_outputs)), 'Multiple writers to one output'
    return nodes, order

def source_check():
    raw = read('input/us-by-role.md')
    lines = [x for x in raw.splitlines() if x.startswith('| US-')]
    keys = [x.split('|')[1].strip() for x in lines]
    assert len(keys) == 18 and set(keys) == SCOPE
    original = (LAB.parents[1] / 'appendix-a-restaurant.md').read_text(encoding='utf-8').splitlines()
    assert all(line in original for line in lines), 'US row differs from appendix'
    return keys

def input_check():
    source_check()
    fr = read('input/fr-nfr-input.md')
    assert 'INPUT_STATUS: MISSING' not in fr, 'FR/NFR input is a pointer, not requirements'
    assert re.search(r'\bFR-[A-Za-z0-9]', fr), 'No real FR identifiers'
    assert SCOPE <= set(re.findall(r'US-\d{2}', fr)), 'Input lacks scoped US references'
    provenance = read('work/input-source.md')
    assert digest('input/fr-nfr-input.md') in provenance, 'Input provenance hash mismatch'
    assert 'รอนักศึกษาระบุ' not in provenance, 'Complete provenance/review status first'
    return fr

def accepted(name):
    lines = read('work/review-record.md').splitlines()
    assert f'ACCEPTED: {name}' in lines, f'Human review missing: {name}'

def node_check(name):
    from jsonschema import Draft202012Validator
    nodes, _ = graph_check()
    assert name in nodes, f'Unknown node: {name}'
    n = nodes[name]
    fr = input_check()
    schema = json.loads(read('input/node-output.schema.json'))
    Draft202012Validator.check_schema(schema)
    data = json.loads(read(f'work/flow-{name}.json'))
    Draft202012Validator(schema).validate(data)
    assert data['node_id'] == name and data['role'] == name
    for out in n['outputs']:
        read(out)
    md = read(f'work/flow-{name}.md')
    sources = {s['path']: s['sha256'] for s in data['sources']}
    assert len(sources) == len(data['sources']), 'Duplicate source'
    required = set(n['inputs']) - {'input/node-output.schema.json'}
    assert required <= sources.keys(), f'Missing sources: {required - sources.keys()}'
    allowed = set(n['inputs']) | {'input/graph.json'}
    for p, sha in sources.items():
        assert p in allowed, f'Unexpected source: {p}'
        assert sha == digest(p), f'Stale/incorrect source hash: {p}'
    flow_ids, coverage = set(), set()
    for f in data['flows']:
        assert f['flow_id'] not in flow_ids, 'Duplicate flow ID'
        flow_ids.add(f['flow_id'])
        assert f['flow_id'] in md, 'Flow absent in Markdown'
        assert set(f['us_refs']) <= SCOPE, 'Out-of-scope US'
        coverage.update(f['us_refs'])
        assert set(f['fr_refs']) <= {e['fr_id'] for e in f['evidence']}
        for e in f['evidence']:
            assert e['fr_id'] in fr and e['quote'] in fr, 'FR evidence not in input'
        for identifier in f['us_refs'] + f['fr_refs']:
            assert identifier in md, f'Markdown missing reference: {identifier}'
    assert ROLES.get(name, SCOPE) <= coverage, 'Incomplete US coverage'
    if name in ROLES:
        assert {f['path_type'] for f in data['flows']} == {'main','alternative','error'}
    for c in data['conflicts_found']:
        assert c['id'] in md, 'Conflict absent in Markdown'
        if c['status'] == 'resolved':
            assert c['fr_refs'] and c['evidence'], 'Resolved without FR evidence'
            assert all(x in fr for x in c['fr_refs']), 'Unknown conflict FR'
            assert all(x in fr for x in c['evidence']), 'Conflict evidence is not verbatim FR'
    if name == 'merge':
        assert all(c['status'] == 'resolved' for c in data['conflicts_found']), 'Unresolved merge: BLOCKED'
    return len(data['flows'])

def ready(name):
    nodes, _ = graph_check()
    input_check()
    read('work/input-audit.md')
    accepted('input')
    for dep in nodes[name]['depends_on']:
        node_check(dep)
        accepted(dep)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--graph', action='store_true')
    p.add_argument('--source', action='store_true')
    p.add_argument('--input', action='store_true')
    p.add_argument('--node')
    p.add_argument('--ready')
    p.add_argument('--all', action='store_true')
    a = p.parse_args()
    try:
        if a.graph:
            print('graph ok:', graph_check()[1])
        if a.source:
            print('verbatim source rows ok:', len(source_check()))
        if a.input:
            input_check()
            print('input mechanical checks ok; human review still required')
        if a.ready:
            ready(a.ready)
            print('dependencies ready:', a.ready)
        if a.node:
            print('node structural checks ok:', a.node, node_check(a.node))
        if a.all:
            for name in graph_check()[1]:
                ready(name)
                print('node structural checks ok:', name, node_check(name))
                accepted(name)
    except Exception as e:
        raise SystemExit(f'BLOCKED: {e}')
