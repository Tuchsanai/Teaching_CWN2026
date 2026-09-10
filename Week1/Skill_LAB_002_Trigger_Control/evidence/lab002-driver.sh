#!/bin/bash
# LAB 002 driver: description variants x test prompts x 2 runs x 2 CLIs, then invocation-control variants.
set -u; export PATH="$HOME/.local/bin:$PATH"; cd /root/skilllab/work
T=/root/skilllab/tools; E=/root/skilllab/evidence/lab002; L=/root/skilllab/labs/002
CS=/root/ai-accounts/.Claude/shared/skills; XS=/root/ai-accounts/.Codex/shared/skills
mkdir -p $E/prompts
declare -A P
P[P1]="ซื้อของ 1500 บาท ต้องจ่ายกี่บาท ตอบสั้น ๆ ไม่ต้องสร้างไฟล์หรือรันคำสั่ง"
P[P2]="ยอด 999 กับ 1000 บาท ได้ส่วนลดไหม ต้องจ่ายเท่าไร ตอบสั้น ๆ ไม่ต้องสร้างไฟล์หรือรันคำสั่ง"
P[P3]="ขอตารางยอดจ่ายสำหรับยอดซื้อ 800 1200 และ 2000 บาท ไม่ต้องสร้างไฟล์หรือรันคำสั่ง"
P[N1]="ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12"
P[N2]="คำว่า ส่วนลด ภาษาอังกฤษคืออะไร ตอบสั้น ๆ ไม่ต้องรันคำสั่ง"
for k in P1 P2 P3 N1 N2; do printf '%s\n' "${P[$k]}" > $E/prompts/$k.txt; done
LIST="มี skill อะไรให้ใช้บ้างในเซสชันนี้ ตอบเป็นรายการชื่อ skill กับคำอธิบายสั้น ๆ ไม่ต้องรันคำสั่ง"
printf '%s\n' "$LIST" > $E/prompts/LIST.txt
MC="/discount ซื้อ 1500 บาท"; MX='$discount ซื้อ 1500 บาท'
printf '%s\n' "$MC" > $E/prompts/MANUAL-claude.txt; printf '%s\n' "$MX" > $E/prompts/MANUAL-codex.txt
inst() { rm -rf $CS/discount $XS/discount; cp -r "$L/$1" $CS/discount; cp -r "$L/${2:-$1}" $XS/discount; echo "== $(date -u +%T) installed claude=$1 codex=${2:-$1}"; }
for v in desc-poor desc-good desc-when; do
  inst $v
  ( for k in P1 P2 P3 N1 N2; do for i in 1 2; do $T/run-claude.sh $E $v-$k-claude-$i yolo1 opus high "${P[$k]}"; done; done ) > $E/$v-claude.summary.jsonl &
  ( for k in P1 P2 P3 N1 N2; do for i in 1 2; do $T/run-codex.sh  $E $v-$k-codex-$i cyolo1 gpt-6-astra medium "${P[$k]}"; done; done ) > $E/$v-codex.summary.jsonl &
  wait
done
# --- invocation control ---
inst no-model
( for i in 1 2; do $T/run-claude.sh $E no-model-P1-claude-$i yolo1 opus high "${P[P1]}"; done
  $T/run-claude.sh $E no-model-MANUAL-claude yolo1 opus high "$MC"
  $T/run-claude.sh $E no-model-LIST-claude yolo1 opus high "$LIST" ) > $E/no-model-claude.summary.jsonl &
( for i in 1 2; do $T/run-codex.sh $E no-model-P1-codex-$i cyolo1 gpt-6-astra medium "${P[P1]}"; done ) > $E/no-model-codex.summary.jsonl &
wait
inst no-user
( for i in 1 2; do $T/run-claude.sh $E no-user-P1-claude-$i yolo1 opus high "${P[P1]}"; done
  $T/run-claude.sh $E no-user-MANUAL-claude yolo1 opus high "$MC"
  $T/run-claude.sh $E no-user-LIST-claude yolo1 opus high "$LIST" ) > $E/no-user-claude.summary.jsonl
inst desc-good codex-explicit
( for i in 1 2; do $T/run-codex.sh $E explicit-P1-codex-$i cyolo1 gpt-6-astra medium "${P[P1]}"; done
  $T/run-codex.sh $E explicit-MANUAL-codex cyolo1 gpt-6-astra medium "$MX"
  $T/run-codex.sh $E explicit-LIST-codex cyolo1 gpt-6-astra medium "$LIST" ) > $E/explicit-codex.summary.jsonl
inst desc-good
date -u +%FT%TZ > $E/DONE; echo "== DONE"
