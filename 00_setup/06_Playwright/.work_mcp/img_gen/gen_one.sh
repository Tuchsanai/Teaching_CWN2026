#!/bin/bash
# usage: gen_one.sh <name> [attempt-suffix]  — prompt from prompts.json (+ optional fix note in fix/<name>.txt)
W=/root/workspace/CWN/Teaching/00_setup/06_Playwright/.work_mcp/img_gen
name=$1; sfx=${2:-v1}
dest="$W/raw/${name%.png}.$sfx.png"
[ -s "$dest" ] && exit 0
prompt=$(python3 -c "import json,sys;print([p['prompt'] for p in json.load(open('$W/prompts.json')) if p['name']=='$name'][0])")
fix=""; [ -f "$W/fix/${name%.png}.txt" ] && fix=" CORRECTIONS FROM PREVIOUS ATTEMPT (must follow): $(cat "$W/fix/${name%.png}.txt")"
cd $W && timeout 1200 cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort="high" -o "$W/out/${name%.png}.$sfx.txt" \
 "${fix:+IMPORTANT: background must be plain pure white (FFFFFF), no dark or gradient areas. }Use the imagegen skill (your built-in image generation tool) to create exactly ONE image, landscape 1536x1024 PNG. Save it exactly to $dest . Do not create or modify any other files. Do not draw anything with code; use the image generation tool. Image description: $prompt$fix" < /dev/null > "$W/out/${name%.png}.$sfx.log" 2>&1
echo "$(date +%T) $name $sfx $( [ -s "$dest" ] && echo OK || echo MISSING)" >> $W/run.log
