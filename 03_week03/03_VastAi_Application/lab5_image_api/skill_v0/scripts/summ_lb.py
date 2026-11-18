import json, sys, os
for name in sys.argv[1:]:
    p = f"/workspace/lab5/results/{name}.json"
    if not os.path.exists(p): print(name, "missing"); continue
    d = json.load(open(p))
    rows = sorted(d["levels"] + d["bisect"], key=lambda r: r["users"])
    cap = d["capacity_users"]
    def share(r):
        g = {}
        for k, v in r["per_replica"].items(): g[k.split("-")[0]] = g.get(k.split("-")[0], 0) + v
        t = sum(g.values()) or 1
        return " ".join(f"{k}={v/t*100:.1f}%" for k, v in sorted(g.items()))
    best = max(rows, key=lambda r: r["throughput_rps"])
    print(f"## {name}: cap={cap}  maxthr={best['throughput_rps']} @N={best['users']}  finished={d.get('finished')}")
    for r in rows:
        print(f"  N={r['users']:<4} {'PASS' if r['pass'] else 'FAIL'} thr={r['throughput_rps']:<6} p50={r['latency_ms']['p50']} p95={r['latency_ms']['p95']} err={r['error_rate']} gpu={r['gpu_util_pct']} batch={r['batch_mean']} | {share(r)}")
