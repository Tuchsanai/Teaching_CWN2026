#!/bin/bash
# usage: run-codex.sh <outdir> <tag> <account:cyoloN> <model> <effort> <prompt> [extra codex exec flags...]
set -u
out=$1; tag=$2; acct=$3; model=$4; effort=$5; prompt=$6; shift 6
export PATH="$HOME/.local/bin:$PATH"
mkdir -p "$out"
s=$(date +%s.%N)
"$acct" exec --skip-git-repo-check -m "$model" -c model_reasoning_effort="$effort" --json -o "$out/$tag.out" "$@" "$prompt" </dev/null > "$out/$tag.jsonl" 2> "$out/$tag.err"
rc=$?
e=$(date +%s.%N)
python3 - "$out/$tag.jsonl" "$out/$tag.out" "$s" "$e" "$rc" "$tag" <<'PY'
import json,sys,re
p,o,s,e,rc,tag=sys.argv[1:7]
cmds=[];usage=None;failed=None;texts=[]
for line in open(p,encoding='utf-8'):
    try: d=json.loads(line)
    except Exception: continue
    it=d.get('item') if isinstance(d.get('item'),dict) else {}
    if d.get('type')=='item.completed' and it.get('type')=='command_execution': cmds.append(str(it.get('command',''))[:200])
    if d.get('type')=='item.completed' and it.get('type')=='agent_message': texts.append(str(it.get('text',''))[:300])
    if d.get('type')=='turn.completed': usage=d.get('usage')
    if d.get('type')=='turn.failed': failed=d.get('error')
try: res=open(o,encoding='utf-8').read()
except Exception: res=''
skill=[c for c in cmds if 'SKILL.md' in c]
print(json.dumps({"tag":tag,"rc":int(rc),"wall_s":round(float(e)-float(s),1),"n_cmds":len(cmds),"cmds":cmds,"skill_reads":skill,
 "usage":usage,"failed":failed,"result":re.sub(r'[\w.+-]+@[\w-]+\.[\w.]+','<email>',res)[:400]},ensure_ascii=False))
PY
