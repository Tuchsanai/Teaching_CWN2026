#!/usr/bin/env bash
# ask-both.sh — ส่งคำถามเดียวกันให้ Claude (yolo2) และ Codex (cyolo1) พร้อมกันแบบขนาน
#
# ใช้งาน:
#   ask-both.sh "<คำถาม>" [--claude-model M] [--claude-effort E]
#                         [--codex-model M]  [--codex-effort E] [--timeout SEC]
#
# ออกแบบให้ exit 0 เสมอ ฝั่งที่ล้มเหลว/ยังไม่ล็อกอินจะรายงานเป็น status ในผลลัพธ์
# ไม่พิมพ์ token, credential หรือ output ของคำสั่งตรวจล็อกอินออกมา

set -u

PROMPT=""
CLAUDE_MODEL="opus"
CLAUDE_EFFORT="high"
CODEX_MODEL="gpt-6-astra"
CODEX_EFFORT="medium"
TIMEOUT_SEC="300"

while [ $# -gt 0 ]; do
  case "$1" in
    --claude-model)  CLAUDE_MODEL="${2:-}"; shift 2 ;;
    --claude-effort) CLAUDE_EFFORT="${2:-}"; shift 2 ;;
    --codex-model)   CODEX_MODEL="${2:-}"; shift 2 ;;
    --codex-effort)  CODEX_EFFORT="${2:-}"; shift 2 ;;
    --timeout)       TIMEOUT_SEC="${2:-}"; shift 2 ;;
    -h|--help)       sed -n '2,12p' "$0"; exit 0 ;;
    *)               [ -z "$PROMPT" ] && PROMPT="$1"; shift ;;
  esac
done

if [ -z "$PROMPT" ]; then
  echo "ask-both.sh: ต้องระบุคำถามเป็นอาร์กิวเมนต์แรก" >&2
  exit 0
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# ---------- ตรวจล็อกอิน (ซ่อน output ทั้งหมด ใช้เฉพาะสถานะ) ----------
claude_logged_in=1
codex_logged_in=1
command -v yolo2  >/dev/null 2>&1 || claude_logged_in=0
command -v cyolo1 >/dev/null 2>&1 || codex_logged_in=0

if [ "$claude_logged_in" = "1" ]; then
  timeout 60 yolo2 auth status --text </dev/null >/dev/null 2>&1 || claude_logged_in=0
fi
if [ "$codex_logged_in" = "1" ]; then
  # หมายเหตุ: cyolo1 login status พิมพ์ข้อความลง stderr จึงต้อง merge 2>&1 ก่อน grep
  timeout 60 cyolo1 login status </dev/null 2>&1 | grep -qi "logged in" || codex_logged_in=0
fi

# ---------- เรียกทั้งสองฝั่งพร้อมกัน ----------
ask_claude() {
  timeout "$TIMEOUT_SEC" yolo2 -p --model "$CLAUDE_MODEL" --effort "$CLAUDE_EFFORT" \
    "$PROMPT" </dev/null >"$WORK/claude.out" 2>"$WORK/claude.err"
  echo $? >"$WORK/claude.rc"
}

ask_codex() {
  timeout "$TIMEOUT_SEC" cyolo1 exec --skip-git-repo-check -m "$CODEX_MODEL" \
    -c model_reasoning_effort="$CODEX_EFFORT" -o "$WORK/codex.out" \
    "$PROMPT" </dev/null >"$WORK/codex.log" 2>&1
  echo $? >"$WORK/codex.rc"
}

pids=""
[ "$claude_logged_in" = "1" ] && { ask_claude & pids="$pids $!"; }
[ "$codex_logged_in"  = "1" ] && { ask_codex  & pids="$pids $!"; }
for p in $pids; do wait "$p" 2>/dev/null; done

# ---------- รายงานผล ----------
emit() { # emit <ชื่อ> <logged_in> <model> <effort> <outfile> <rcfile>
  local label="$1" ok="$2" model="$3" effort="$4" out="$5" rcf="$6" rc status
  echo "=== $label ==="
  echo "model: $model"
  echo "effort: $effort"
  if [ "$ok" != "1" ]; then
    echo "status: skipped"
    echo "reason: ข้าม (ยังไม่ล็อกอิน)"
    echo "answer:"
    echo "(ไม่มีคำตอบ)"
    return
  fi
  rc="$(cat "$rcf" 2>/dev/null || echo 1)"
  case "$rc" in
    0)   status="ok" ;;
    124) status="error"; echo "status: error"; echo "reason: หมดเวลา (${TIMEOUT_SEC}s)" ;;
    *)   status="error"; echo "status: error"; echo "reason: คำสั่งจบด้วย exit code $rc" ;;
  esac
  [ "$status" = "ok" ] && echo "status: ok"
  echo "answer:"
  if [ -s "$out" ]; then cat "$out"; else echo "(ไม่มีคำตอบ)"; fi
  echo
}

emit "CLAUDE (yolo2)" "$claude_logged_in" "$CLAUDE_MODEL" "$CLAUDE_EFFORT" "$WORK/claude.out" "$WORK/claude.rc"
emit "CODEX (cyolo1)" "$codex_logged_in"  "$CODEX_MODEL"  "$CODEX_EFFORT"  "$WORK/codex.out"  "$WORK/codex.rc"

exit 0
