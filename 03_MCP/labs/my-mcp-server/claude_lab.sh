#!/usr/bin/env bash
# claude_lab.sh — ส่ง prompt ของนักศึกษาให้ Claude Code (โหมด -p) พร้อม MCP server ของเรา แล้วเก็บหลักฐาน
# ใช้:  ./claude_lab.sh <ชื่อรอบ> <โฟลเดอร์หลักฐาน> "<prompt>"
# ต้องการ: โปรไฟล์ Claude Code ที่ล็อกอินแล้วใน $CLAUDE_CONFIG_DIR (ค่าเริ่มต้น yolo1)
set -uo pipefail
NAME="$1"; OUT="$2"; PROMPT="$3"
HERE="$(cd "$(dirname "$0")" && pwd)"
export CLAUDE_CONFIG_DIR="${CLAUDE_CONFIG_DIR:-/root/workspace/.Claude/yolo1}"
MODEL="${MODEL:-sonnet}"; EFFORT="${EFFORT:-medium}"
rm -f "$HERE/wire-claude-hello.jsonl" "$HERE/wire-claude-tts.jsonl"   # เริ่ม log บนสายใหม่ทุกรอบ
mkdir -p "$OUT"
printf '%s\n' "$PROMPT" > "$OUT/claude-$NAME-prompt.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$OUT/claude-$NAME-start-utc.txt"
cd "$HERE"
env IS_SANDBOX=1 claude --dangerously-skip-permissions -p \
  --model "$MODEL" --effort "$EFFORT" \
  --strict-mcp-config --mcp-config "$HERE/mcp.json" \
  --output-format stream-json --verbose \
  "$PROMPT" < /dev/null > "$OUT/claude-$NAME-stream.jsonl" 2> "$OUT/claude-$NAME-stderr.txt"
echo "exit=$?" > "$OUT/claude-$NAME-exit.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$OUT/claude-$NAME-end-utc.txt"
[ -f "$HERE/wire-claude-hello.jsonl" ] && mv "$HERE/wire-claude-hello.jsonl" "$OUT/claude-$NAME-wire-hello.jsonl"
[ -f "$HERE/wire-claude-tts.jsonl" ] && mv "$HERE/wire-claude-tts.jsonl" "$OUT/claude-$NAME-wire-tts.jsonl"
echo "done $NAME: $(cat "$OUT/claude-$NAME-exit.txt") lines=$(wc -l < "$OUT/claude-$NAME-stream.jsonl")"
