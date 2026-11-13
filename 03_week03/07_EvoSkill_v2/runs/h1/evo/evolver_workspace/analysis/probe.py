# usage: python3 -I probe.py <solver_dir> <probes.json>  -> prints outputs per probe
import sys, json, subprocess
solver_dir, probes = sys.argv[1], json.load(open(sys.argv[2]))
for kw in probes:
    p = subprocess.run([sys.executable, '-I', solver_dir + '/solve.py'], input=json.dumps(kw), capture_output=True, text=True, timeout=10)
    print(json.dumps(kw, ensure_ascii=False), '->', (p.stdout.strip() or p.stderr.strip()[-120:]).replace('\n',' '), 'rc=%d' % p.returncode)
