#!/bin/bash
# usage: runtest.sh <lab> [tag]  — run prompt with yolo2 sonnet inside the student container, copy /workspace back
W=/root/workspace/CWN/Teaching/00_setup/.work/06_pwcli/v2; C=${C:-pwcli-lab06-test}; L=$1; T=${2:-$1}
docker cp $W/prompts/$L.txt $C:/tmp/prompt.txt
start=$(date +%s)
docker exec $C bash -lc 'cd /workspace && timeout 1800 yolo2 -p --model sonnet "$(cat /tmp/prompt.txt)"' > $W/tests/$T.out 2>&1
rc=$?
echo "rc=$rc secs=$(( $(date +%s)-start ))" >> $W/tests/$T.out
rm -rf $W/scratch/$T; mkdir -p $W/scratch/$T; docker cp $C:/workspace/. $W/scratch/$T/ >/dev/null
echo "$T rc=$rc secs=$(( $(date +%s)-start ))"
