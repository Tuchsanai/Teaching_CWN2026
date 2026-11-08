"""compare.py <new_label> [old_label] : compare benchmark results, print table + verdict (JSON on last line)."""
import glob, json, statistics as st, sys, os

R = "C:/t/s04b/eval/results"
new, old = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "old")


def load(label):
    out = {}
    for f in sorted(glob.glob(f"{R}/{label}-B*-*.verify.json")):
        b = os.path.basename(f).split("-")[1]
        try:
            v = json.load(open(f, encoding="utf-8"))
        except ValueError:
            v = {"wall_s": None, "tool_calls": None, "tool_errors": None, "cost_usd": None, "checks": {"pass": False}}
        out.setdefault(b, []).append(v)
    return out


def med(xs, k):
    vals = [x[k] for x in xs if x.get(k) is not None]
    return round(st.median(vals), 2) if vals else None


O, N = load(old), load(new)
rows, ok, better = [], True, False
for b in ("B1", "B2", "B3"):
    o, n = O.get(b, []), N.get(b, [])
    if not n:
        ok = False; continue
    po = all(x["checks"].get("pass") for x in o) if o else None
    pn = all(x["checks"].get("pass") for x in n)
    r = {"bench": b, "old_pass": po, "new_pass": pn}
    for k in ("wall_s", "tool_calls", "tool_errors", "cost_usd"):
        r["old_" + k], r["new_" + k] = med(o, k), med(n, k)
    rows.append(r)
    if not pn:
        ok = False
    tol = 1.10 if b == "B1" else 1.25
    if r["old_wall_s"] and r["new_wall_s"] > r["old_wall_s"] * tol:
        ok = False
    if r["old_tool_calls"] is not None and r["new_tool_calls"] > r["old_tool_calls"] + (0 if b == "B1" else 3):
        ok = False
    if r["old_tool_errors"] is not None and r["new_tool_errors"] > r["old_tool_errors"] + (0 if b == "B1" else 1):
        ok = False
    if r["old_wall_s"] and (r["new_wall_s"] <= r["old_wall_s"] * 0.9 or r["new_tool_calls"] <= r["old_tool_calls"] * 0.9):
        better = True

print("| bench | pass old→new | wall s | app commands | failed commands | cost $ |")
print("|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r['bench']} | {r['old_pass']}→{r['new_pass']} | {r['old_wall_s']}→{r['new_wall_s']} | {r['old_tool_calls']}→{r['new_tool_calls']} | {r['old_tool_errors']}→{r['new_tool_errors']} | {r['old_cost_usd']}→{r['new_cost_usd']} |")
print(json.dumps({"not_worse": ok, "better": ok and better, "rows": rows}, ensure_ascii=False))
