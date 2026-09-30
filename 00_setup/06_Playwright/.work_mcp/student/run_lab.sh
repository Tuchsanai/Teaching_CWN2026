#!/bin/bash
# รัน LAB N แบบนักศึกษาใน container: bash run_lab.sh N [tag]
set -u
N=$1; TAG=${2:-}; C=devtools-pwmcp-c34a6add
D=/root/workspace/CWN/Teaching/00_setup/06_Playwright/.work_mcp/student
cd $D
python3 extract_prompt.py $N > lab$N$TAG.prompt.txt
docker cp lab$N$TAG.prompt.txt $C:/tmp/lab$N.prompt.txt
echo "$(date +%T) START lab$N$TAG" >> runs.log
S=$(date +%s)
docker exec $C bash -lc 'cd /workspace && yolo1 -p --model sonnet --output-format json "$(cat /tmp/lab'$N'.prompt.txt)" < /dev/null' > lab$N$TAG.json 2> lab$N$TAG.err
RC=$?
E=$(date +%s)
python3 - "$D/lab$N$TAG.json" $RC $((E-S)) <<'PY' >> runs.log
import json,sys
p,rc,sec=sys.argv[1:]
try:
    j=json.load(open(p)); print(f"lab rc={rc} wall={sec}s is_error={j.get('is_error')} turns={j.get('num_turns')} cost={j.get('total_cost_usd')} dur_ms={j.get('duration_ms')}")
except Exception as e: print(f"lab rc={rc} wall={sec}s parse error {e}")
PY
echo "$(date +%T) END lab$N$TAG" >> runs.log
# คัดผลกลับ
mkdir -p ws_after_lab$N$TAG
docker exec $C bash -lc 'cd /workspace && tar --exclude=./mcp-out -cf - .' | tar -xf - -C ws_after_lab$N$TAG
docker exec $C bash -lc 'ps -eo pid,cmd | grep -E "[c]hrom|[p]laywright-mcp|[c]li-client" | cut -c1-150' > procs_after_lab$N$TAG.txt
