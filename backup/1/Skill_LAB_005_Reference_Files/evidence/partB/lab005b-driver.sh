#!/bin/bash
set -u; export PATH="$HOME/.local/bin:$PATH"; cd /root/skilllab/work
T=/root/skilllab/tools; E=/root/skilllab/evidence/lab005b; L=/root/skilllab/labs/005
CS=/root/ai-accounts/.Claude/shared/skills; XS=/root/ai-accounts/.Codex/shared/skills
mkdir -p $E; for s in discount accounts shop-rules cheap-check vat second-opinion second-opinion-ai; do rm -rf $CS/$s $XS/$s; done
Q2="คืนสินค้าได้ภายในกี่วัน มีเงื่อนไขอะไร ตอบสั้น ๆ ไม่ต้องสร้างไฟล์"; Q1="ซื้อของ 1200 บาท ส่งแบบธรรมดา ต้องจ่ายรวมค่าส่งเท่าไร ตอบสั้น ๆ ไม่ต้องสร้างไฟล์"
for v in shop-rules-big shop-rules-mono-big; do
  rm -rf $CS/shop-rules $XS/shop-rules; cp -r $L/$v $CS/shop-rules; cp -r $L/$v $XS/shop-rules; echo "== $(date -u +%T) installed $v"
  ( for i in 1 2; do $T/run-claude.sh $E $v-Q2-claude-$i yolo1 opus high "$Q2"; $T/run-claude.sh $E $v-Q1-claude-$i yolo1 opus high "$Q1"; done ) > $E/$v-claude.summary.jsonl &
  ( for i in 1 2; do $T/run-codex.sh  $E $v-Q2-codex-$i cyolo1 gpt-6-astra medium "$Q2"; $T/run-codex.sh $E $v-Q1-codex-$i cyolo1 gpt-6-astra medium "$Q1"; done ) > $E/$v-codex.summary.jsonl &
  wait
done
rm -rf $CS/shop-rules $XS/shop-rules
date -u +%FT%TZ > $E/DONE
