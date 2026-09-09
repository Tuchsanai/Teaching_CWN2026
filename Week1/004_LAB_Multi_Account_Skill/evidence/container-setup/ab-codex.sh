#!/bin/bash
# usage: ab-codex.sh <tag> <prompt-file> ; runs cyolo1 exec (astra/medium) once with --json, records events
set -u; tag=$1; pf=$2; cd /root/lab004; mkdir -p ab; export PATH="$HOME/.local/bin:$PATH"
s=$(date +%s.%N)
cyolo1 exec --skip-git-repo-check --model gpt-6-astra -c model_reasoning_effort=medium --json -o "ab/$tag.out" "$(cat "$pf")" </dev/null > "ab/$tag.jsonl" 2> "ab/$tag.err"
e=$(date +%s.%N)
python3 - "ab/$tag.jsonl" "ab/$tag.out" "$s" "$e" <<'PY'
import json,sys
cmds=[];usage=None;failed=None
for line in open(sys.argv[1]):
    try: d=json.loads(line)
    except Exception: continue
    it=d.get("item") if isinstance(d.get("item"),dict) else {}
    if d.get("type")=="item.completed" and it.get("type")=="command_execution": cmds.append(str(it.get("command",""))[:160])
    if d.get("type")=="turn.completed": usage=d.get("usage")
    if d.get("type")=="turn.failed": failed=d.get("error")
try: out=open(sys.argv[2]).read()
except Exception: out=""
print(json.dumps({"wall_s":round(float(sys.argv[4])-float(sys.argv[3]),1),"n_cmds":len(cmds),"cmds":cmds,"usage":usage,"failed":failed,"result":out[:600]},ensure_ascii=False))
PY
