#!/bin/bash
# run-app.sh <out_name> <prompt_file>  : host Claude Code (stand-in for the Claude Code app), scoped permissions
out=$1; pf=$2; cd /c/t/s04b/app
s=$(date +%s.%N)
claude -p "$(cat $pf)" --model opus --effort medium --permission-mode acceptEdits \
  --allowedTools "Bash(docker cp:*)" "Bash(docker exec:*)" "Bash(docker ps:*)" "Bash(docker:*)" "Bash(MSYS_NO_PATHCONV=1 docker:*)" "Read" "Glob" "Grep" \
  --output-format stream-json --verbose < /dev/null > $out.jsonl 2> $out.err
e=$(date +%s.%N)
PYTHONIOENCODING=utf-8 python C:/t/s04b/eval/metrics.py $out.jsonl $s $e > $out.metrics.json
