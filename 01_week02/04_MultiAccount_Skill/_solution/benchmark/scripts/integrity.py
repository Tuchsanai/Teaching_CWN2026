"""integrity.py <step1.jsonl> : list every builder action that touched old-skill material (proof of 'from scratch')."""
import json, re, sys

PAT = re.compile(r"t/s04/|t\\s04\\|skills-old|s04b/eval|_solution|reference/|\.skill-backup|swarm\.py|Teaching|/projects/", re.I)
hits, n = [], 0
for l in open(sys.argv[1], encoding="utf-8"):
    try:
        m = json.loads(l)
    except ValueError:
        continue
    if m.get("type") != "assistant":
        continue
    for c in m["message"].get("content", []):
        if c.get("type") == "tool_use":
            n += 1
            s = json.dumps(c["input"], ensure_ascii=False)
            for x in PAT.finditer(s):
                hits.append(x.group(0) + " :: " + s[max(0, x.start() - 80): x.end() + 40])
print(json.dumps({"tool_calls": n, "old_material_hits": hits}, ensure_ascii=False, indent=1))
