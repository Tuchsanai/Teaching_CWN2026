#!/bin/bash
# usage: ab-claude.sh <tag> <prompt-file> ; runs yolo1 -p (opus/high) once, records JSON + session commands
set -u; tag=$1; pf=$2; cd /root/lab004; mkdir -p ab; export PATH="$HOME/.local/bin:$PATH"
before=$(ls /root/ai-accounts/.Claude/yolo1/projects/-root-lab004/*.jsonl 2>/dev/null | sort)
s=$(date +%s.%N)
yolo1 -p --model opus --effort high --output-format json "$(cat "$pf")" </dev/null > "ab/$tag.json" 2> "ab/$tag.err"
e=$(date +%s.%N)
after=$(ls /root/ai-accounts/.Claude/yolo1/projects/-root-lab004/*.jsonl 2>/dev/null | sort)
new=$(comm -13 <(echo "$before") <(echo "$after") | head -1)
printf '%s\n' "$new" > "ab/$tag.session"
python3 - "ab/$tag.json" "$s" "$e" <<'PY'
import json,sys
d=json.load(open(sys.argv[1])); wall=float(sys.argv[3])-float(sys.argv[2])
print(json.dumps({"wall_s":round(wall,1),"duration_ms":d.get("duration_ms"),"num_turns":d.get("num_turns"),"cost":d.get("total_cost_usd"),"is_error":d.get("is_error"),"result":str(d.get("result",""))[:600]},ensure_ascii=False))
PY
