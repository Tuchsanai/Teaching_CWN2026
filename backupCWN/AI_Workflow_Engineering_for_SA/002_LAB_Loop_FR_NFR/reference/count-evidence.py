#!/usr/bin/env python3
"""Count document rows and recorded usage; run from the LAB directory."""
import json
import re
from pathlib import Path

SCOPE = {'US-' + x for x in '01 02 03 04 05 06 07 08 10 11 12 13 15 16 19 20 25 26'.split()}


def document(path, scope=None):
    """An AC unit is one FR table AC cell, not every predicate within it.

    Count a numeric AC only after removing identifier references, so US/FR
    numbers are not mistaken for measurable quantities. Match the US column
    only; dependencies in business-rule cells do not extend the scope.
    """
    rows = []
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) != 5 or not re.fullmatch(r'FR-\d+(?:[.-]\d+)?', cells[0]):
            continue
        us = set(re.findall(r'US-\d+', cells[1]))
        if scope is None or us & scope:
            rows.append((cells, us))
    assert rows, f'No five-column FR rows in {path}'
    identifiers = [cells[0] for cells, _ in rows]
    assert len(identifiers) == len(set(identifiers)), 'Duplicate FR identifiers'
    numeric = []
    for cells, _ in rows:
        ac = re.sub(r'\b(?:US|FR|NFR|AC|Q|DI)-[\w.-]+', '', cells[3])
        if re.search(r'[0-9๐-๙]', ac):
            numeric.append(cells[0])
    return dict(fr_count=len(rows), us_with_fr=len(set().union(*(u for _, u in rows))),
                numeric_ac_cells=len(numeric), numeric_ac_fr_ids=numeric,
                fr_ids=identifiers)


def usage(log):
    events = [json.loads(line) for line in Path(log).read_text().splitlines() if line.strip()]
    assert not any(e.get('type') == 'turn.failed' for e in events), log
    return [e['usage'] for e in events if e.get('type') == 'turn.completed'][-1]


def main():
    baseline = Path('../001_LAB_Single_Prompt_Baseline/reference')
    source = baseline / 'step-02/round-1/fr-nfr-v0.md'
    loop = json.loads(Path('reference/loop-log.json').read_text())
    final = Path(loop['final_document'])
    calls = []
    for log in sorted(baseline.glob('step-*/round-1/log.jsonl')):
        u = usage(log)
        m = json.loads(log.with_name('run-meta.json').read_text())
        calls.append(dict(log=str(log), input_tokens=u['input_tokens'],
                          output_tokens=u['output_tokens'], duration_s=m['end_epoch']-m['start_epoch']))
    result = dict(baseline_full=document(source), baseline_common=document(source, SCOPE),
                  final_full=document(final), final_common=document(final, SCOPE),
                  baseline_calls=calls,
                  baseline_total_tokens=sum(c['input_tokens']+c['output_tokens'] for c in calls),
                  baseline_duration_s=sum(c['duration_s'] for c in calls),
                  loop_total_tokens=sum(c['input_tokens']+c['output_tokens'] for c in loop['rounds']),
                  loop_duration_s=sum(c['duration_s'] for c in loop['rounds']))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
