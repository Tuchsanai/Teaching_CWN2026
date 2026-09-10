#!/bin/bash
# LAB 002 part B: (1) Codex matrix with prompts that do NOT forbid running commands; (2) competing skill (distractor) test.
set -u; export PATH="$HOME/.local/bin:$PATH"; cd /root/skilllab/work
T=/root/skilllab/tools; E=/root/skilllab/evidence/lab002b; L=/root/skilllab/labs/002
CS=/root/ai-accounts/.Claude/shared/skills; XS=/root/ai-accounts/.Codex/shared/skills
mkdir -p $E/prompts
for s in discount accounts shop-rules cheap-check vat; do rm -rf $CS/$s $XS/$s; done
declare -A P
P[P1]="ซื้อของ 1500 บาท ต้องจ่ายกี่บาท ตอบสั้น ๆ ไม่ต้องสร้างไฟล์"
P[P2]="ยอด 999 กับ 1000 บาท ได้ส่วนลดไหม ต้องจ่ายเท่าไร ตอบสั้น ๆ ไม่ต้องสร้างไฟล์"
P[P3]="ขอตารางยอดจ่ายสำหรับยอดซื้อ 800 1200 และ 2000 บาท ไม่ต้องสร้างไฟล์"
P[N1]="ตอบเป็นตัวเลขล้วนอย่างเดียว: 12*12"
P[N2]="คำว่า ส่วนลด ภาษาอังกฤษคืออะไร ตอบสั้น ๆ"
for k in P1 P2 P3 N1 N2; do printf '%s\n' "${P[$k]}" > $E/prompts/$k.txt; done
inst() { rm -rf $CS/discount $XS/discount; cp -r "$L/$1" $CS/discount; cp -r "$L/$1" $XS/discount; echo "== $(date -u +%T) installed $1"; }
# (1) Codex matrix, commands allowed
for v in desc-poor desc-good desc-when; do
  inst $v
  ( for k in P1 P2 P3 N1 N2; do for i in 1 2; do $T/run-codex.sh $E $v-$k-codex-$i cyolo1 gpt-6-astra medium "${P[$k]}"; done; done ) > $E/$v-codex.summary.jsonl
done
# (2) distractor: vat skill competes with discount
cp -r $L/vat $CS/vat; cp -r $L/vat $XS/vat
for v in desc-poor desc-good; do
  inst $v; echo "== with distractor vat"
  ( for i in 1 2; do $T/run-claude.sh $E dis-$v-P1-claude-$i yolo1 opus high "${P[P1]}"; done ) > $E/dis-$v-claude.summary.jsonl &
  ( for i in 1 2; do $T/run-codex.sh  $E dis-$v-P1-codex-$i cyolo1 gpt-6-astra medium "${P[P1]}"; done ) > $E/dis-$v-codex.summary.jsonl &
  wait
done
rm -rf $CS/vat $XS/vat; inst desc-good
date -u +%FT%TZ > $E/DONE
