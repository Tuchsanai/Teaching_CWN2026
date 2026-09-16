#!/bin/bash
# usage: ask-both.sh "<question>"   -> asks yolo2 (Claude) and cyolo1 (Codex) in parallel, prints both answers.
# Exit 0 even if one side fails; each side reports its own status. Never prints credentials.
set -u
export PATH="$HOME/.local/bin:$PATH"
q=${1:?question required}
d=$(mktemp -d /tmp/second-opinion.XXXXXX)
CM=${CLAUDE_MODEL:-opus}; CE=${CLAUDE_EFFORT:-high}; XM=${CODEX_MODEL:-gpt-6-astra}; XE=${CODEX_EFFORT:-medium}
if yolo2 auth status --text </dev/null >/dev/null 2>&1; then
  ( yolo2 -p --model "$CM" --effort "$CE" --output-format json "$q ตอบสั้น ๆ ไม่ต้องสร้างไฟล์หรือรันคำสั่ง" </dev/null \
      | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d.get("result",""));print("__COST__",d.get("total_cost_usd"))' > "$d/claude.txt" 2>"$d/claude.err" ) &
  pc=$!
else
  echo "yolo2 ยังไม่ล็อกอิน" > "$d/claude.txt"; pc=""
fi
if cyolo1 login status </dev/null 2>&1 | grep -q '^Logged in'; then
  ( cyolo1 exec --skip-git-repo-check -m "$XM" -c model_reasoning_effort="$XE" -o "$d/codex.txt" "$q ตอบสั้น ๆ ไม่ต้องสร้างไฟล์หรือรันคำสั่ง" </dev/null >"$d/codex.log" 2>&1 ) &
  px=$!
else
  echo "cyolo1 ยังไม่ล็อกอิน" > "$d/codex.txt"; px=""
fi
[ -n "$pc" ] && wait $pc; [ -n "$px" ] && wait $px
echo "=== Claude (yolo2, $CM/$CE) ==="; cat "$d/claude.txt" 2>/dev/null || echo "(ไม่มีคำตอบ)"
echo "=== Codex (cyolo1, $XM/$XE) ==="; cat "$d/codex.txt" 2>/dev/null || echo "(ไม่มีคำตอบ)"
exit 0
