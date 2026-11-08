"""phase.py <label...> : split each run's app commands into discovery (before first SKILL.md read) and skill phase; count errors in each."""
import glob, json, os, sys

R = "C:/t/s04b/eval/results"
for label in sys.argv[1:]:
    for f in sorted(glob.glob(f"{R}/{label}-B*-*.jsonl")):
        calls, order, errs = {}, [], set()
        for l in open(f, encoding="utf-8"):
            try:
                m = json.loads(l)
            except ValueError:
                continue
            if m.get("type") == "assistant":
                for c in m["message"].get("content", []):
                    if c.get("type") == "tool_use":
                        calls[c["id"]] = json.dumps(c["input"], ensure_ascii=False)
                        order.append(c["id"])
            if m.get("type") == "user":
                for c in m["message"].get("content", []):
                    if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"):
                        errs.add(c["tool_use_id"])
        first = next((i for i, k in enumerate(order) if "SKILL.md" in calls[k]), len(order))
        d, s = order[:first], order[first:]
        print(f"{os.path.basename(f)[:-6]:14} discovery {len(d):2} cmds/{sum(k in errs for k in d)} err | skill phase {len(s):2} cmds/{sum(k in errs for k in s)} err")
