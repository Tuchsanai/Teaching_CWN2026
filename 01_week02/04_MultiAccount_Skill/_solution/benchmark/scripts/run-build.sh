#!/bin/bash
# run-build.sh <iter> : step 1 (build skills from spec + hints, no reference) in a fresh folder, then copy skills out
source /c/t/s04b/eval/lib.sh
it=$1; B=/c/t/msb-iter$it; D=$B/04_MultiAccount_Skill
mkdir -p $D && cp /c/t/s04b/inputs/prompt_skill_spec.md /c/t/s04b/inputs/prompt_skill_hints.md $D/
cp /c/t/s04b/inputs/step1-prompt.txt $B/step1-prompt.txt
echo "$(date +%T) BUILD-START iter$it" >> /c/t/s04b/logs/events.log
install_skills ""          # container has NO yolo/cyolo/agent-team skills before the build
reset_ws
cd $D; s=$(date +%s.%N)
unset MSYS_NO_PATHCONV
claude -p "$(cat ../step1-prompt.txt)" --model opus --effort medium --permission-mode acceptEdits \
  --allowedTools "Bash" "PowerShell" "Read" "Glob" "Grep" "Write" "Edit" \
  --output-format stream-json --verbose < /dev/null > ../step1.jsonl 2> ../step1.err
e=$(date +%s.%N)
PYTHONIOENCODING=utf-8 python C:/t/s04b/eval/metrics.py C:/t/msb-iter$it/step1.jsonl $s $e > ../step1.metrics.json
mkdir -p ../ws && MSYS_NO_PATHCONV=1 docker cp multi-account:/workspace/. ../ws/ >/dev/null 2>&1
echo "$(date +%T) BUILD-END iter$it $(python -c "import json;m=json.load(open(r'C:/t/msb-iter$it/step1.metrics.json',encoding='utf-8'));print({k:m[k] for k in ('wall_s','tool_calls','tool_errors','cost_usd','is_error')})")" >> /c/t/s04b/logs/events.log
