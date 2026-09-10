#!/bin/bash
set -u; export PATH="$HOME/.local/bin:$PATH"; cd /root/skilllab/work
T=/root/skilllab/tools; E=/root/skilllab/evidence/lab005; L=/root/skilllab/labs/005
CS=/root/ai-accounts/.Claude/shared/skills; XS=/root/ai-accounts/.Codex/shared/skills
mkdir -p $E/prompts
rm -rf $CS/accounts $XS/accounts
declare -A P
P[Q1]="ซื้อของ 1200 บาท ส่งแบบธรรมดา ต้องจ่ายรวมค่าส่งเท่าไร ตอบสั้น ๆ ไม่ต้องสร้างไฟล์"
P[Q2]="คืนสินค้าได้ภายในกี่วัน มีเงื่อนไขอะไร ตอบสั้น ๆ ไม่ต้องสร้างไฟล์"
P[Q3]="สมาชิก Gold ซื้อของ 2000 บาท ต้องจ่ายค่าสินค้าเท่าไร ตอบสั้น ๆ ไม่ต้องสร้างไฟล์"
for k in Q1 Q2 Q3; do printf '%s\n' "${P[$k]}" > $E/prompts/$k.txt; done
for v in shop-rules shop-rules-mono; do
  rm -rf $CS/shop-rules $XS/shop-rules; cp -r $L/$v $CS/shop-rules; cp -r $L/$v $XS/shop-rules; echo "== $(date -u +%T) installed $v"
  ( for k in Q1 Q2 Q3; do for i in 1 2; do $T/run-claude.sh $E $v-$k-claude-$i yolo1 opus high "${P[$k]}"; done; done ) > $E/$v-claude.summary.jsonl &
  ( for k in Q1 Q2 Q3; do for i in 1 2; do $T/run-codex.sh $E $v-$k-codex-$i cyolo1 gpt-6-astra medium "${P[$k]}"; done; done ) > $E/$v-codex.summary.jsonl &
  wait
done
rm -rf $CS/shop-rules $XS/shop-rules; cp -r $L/shop-rules $CS/shop-rules; cp -r $L/shop-rules $XS/shop-rules
date -u +%FT%TZ > $E/DONE
