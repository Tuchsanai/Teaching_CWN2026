# Rebuild each Solver's final solve.py from its trace (Write, then Edit ops in order)
# and run the reference unit tests against it. Output goes to analysis/replay/.
import json, os, sys, glob, shutil, subprocess
TRACES = '/evo/traces/epoch_0'
OUT = '/evo/evolver_workspace/analysis/replay'
REF = '/evo/reference/answers'
results = {}
for path in sorted(glob.glob(f'{TRACES}/*.jsonl')):
    name = os.path.basename(path)[:-6]
    task = name.split('_')[0] + '_' + name.split('_')[1] if False else name.rsplit('_s', 1)[0]
    ref_dir = {'t1-cafe-bill': 't1-cafe-bill', 't2-split-bill': 't2-split-bill',
               't3-shipping-fee': 't3-shipping-fee', 't4-cashback': 't4-cashback'}[task]
    src = None
    for line in open(path, encoding='utf-8'):
        o = json.loads(line)
        for b in (o.get('message', {}).get('content') or []):
            if isinstance(b, dict) and b.get('type') == 'tool_use':
                inp = b.get('input', {})
                if b['name'] == 'Write' and str(inp.get('file_path', '')).endswith('solve.py'):
                    src = inp['content']
                elif b['name'] == 'Edit' and str(inp.get('file_path', '')).endswith('solve.py') and src is not None:
                    if inp['old_string'] in src:
                        src = src.replace(inp['old_string'], inp['new_string'], 1)
    d = f'{OUT}/{name}'
    os.makedirs(d, exist_ok=True)
    open(f'{d}/solve.py', 'w', encoding='utf-8').write(src or '')
    shutil.copy(f'{REF}/{ref_dir}/test_solve.py', f'{d}/test_solve.py')
    # run in isolated mode, with the solver dir put on sys.path explicitly
    runner = ('import sys, unittest; sys.path.insert(0, sys.argv[1]); '
              'suite = unittest.defaultTestLoader.discover(sys.argv[1], pattern="test_solve.py"); '
              'r = unittest.TextTestRunner(stream=open(sys.argv[1]+"/run.log","w"), verbosity=2).run(suite); '
              'print(r.testsRun, len(r.failures), len(r.errors))')
    p = subprocess.run([sys.executable, '-I', '-c', runner, d], capture_output=True, text=True, timeout=60)
    log = open(f'{d}/run.log', encoding='utf-8').read()
    fails = [l.strip() for l in log.splitlines() if (' ... FAIL' in l or ' ... ERROR' in l)]
    results[name] = {'summary': p.stdout.strip() or p.stderr.strip()[-300:], 'fails': fails}
for k, v in results.items():
    print(k, '| testsRun/failures/errors =', v['summary'])
    for f in v['fails']:
        print('     ', f)
