#!/bin/bash
# usage: run-claude.sh <outdir> <tag> <account:yoloN> <model> <effort> <prompt> [extra claude flags...]
# Runs yoloN -p (json), keeps stdout/stderr, finds the new session jsonl, dumps a readable transcript + tool list.
set -u
out=$1; tag=$2; acct=$3; model=$4; effort=$5; prompt=$6; shift 6
export PATH="$HOME/.local/bin:$PATH"
mkdir -p "$out"
cfg="/root/ai-accounts/.Claude/$acct"
proj="$cfg/projects/$(pwd | sed 's#/#-#g')"
before=$(ls "$proj"/*.jsonl 2>/dev/null | sort)
s=$(date +%s.%N)
"$acct" -p --model "$model" --effort "$effort" --output-format json "$prompt" "$@" </dev/null > "$out/$tag.json" 2> "$out/$tag.err"
rc=$?
e=$(date +%s.%N)
after=$(ls "$proj"/*.jsonl 2>/dev/null | sort)
new=$(comm -13 <(echo "$before") <(echo "$after") | head -1)
[ -n "$new" ] && cp "$new" "$out/$tag.session.jsonl"
python3 /root/skilllab/tools/claude-transcript.py "$out/$tag.session.jsonl" > "$out/$tag.transcript.txt" 2>/dev/null
python3 - "$out/$tag.json" "$s" "$e" "$rc" "$tag" "$out/$tag.transcript.txt" <<'PY'
import json,sys,re
p,s,e,rc,tag,tr=sys.argv[1:7]
try: d=json.load(open(p))
except Exception as ex: d={"result":"<no json: %s>"%ex}
try: t=open(tr,encoding="utf-8").read()
except Exception: t=""
skills=re.findall(r'TOOL \d+ Skill: (\{.*?\})',t)
tools=re.findall(r'TOOL \d+ (\w+):',t)
mu=d.get("modelUsage",{}) or {}
print(json.dumps({"tag":tag,"rc":int(rc),"wall_s":round(float(e)-float(s),1),"duration_ms":d.get("duration_ms"),
 "num_turns":d.get("num_turns"),"cost":d.get("total_cost_usd"),"is_error":d.get("is_error"),
 "models":sorted(mu.keys()),"tools":tools,"skills":skills,"result":str(d.get("result",""))[:400]},ensure_ascii=False))
PY
