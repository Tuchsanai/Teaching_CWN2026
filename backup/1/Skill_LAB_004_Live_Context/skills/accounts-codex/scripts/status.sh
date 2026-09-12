#!/bin/bash
# Print login status of every account as a table row. Always exits 0 (a skill's !`command` aborts on non-zero exit).
export PATH="$HOME/.local/bin:$PATH"
for n in 1 2 3 4 5; do
  if "yolo$n" auth status --text </dev/null >/dev/null 2>&1; then s="ล็อกอินแล้ว"; else s="ยังไม่ล็อกอิน"; fi
  echo "| yolo$n | Claude Code | $s |"
done
for n in 1 2 3 4 5; do
  if "cyolo$n" login status </dev/null 2>&1 | grep -q '^Logged in'; then s="ล็อกอินแล้ว"; else s="ยังไม่ล็อกอิน"; fi
  echo "| cyolo$n | Codex CLI | $s |"
done
exit 0
