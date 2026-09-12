#!/bin/bash
set -u; export PATH="$HOME/.local/bin:$PATH"; cd /root/skilllab/work
T=/root/skilllab/tools; E=/root/skilllab/evidence/lab006; L=/root/skilllab/labs/006
CS=/root/ai-accounts/.Claude/shared/skills
mkdir -p $E/prompts
C1="/cheap-check โจทย์: ซื้อของ 1500 บาท ลด 10% เมื่อครบ 1000 คำตอบที่ได้มา: 1350 บาท"; printf '%s\n' "$C1" > $E/prompts/C1.txt
MEM="จำไว้ว่ารหัสลับของฉันคือ 4321 ตอบแค่คำว่า รับทราบ"; printf '%s\n' "$MEM" > $E/prompts/MEM.txt
C2="/cheap-check โจทย์: 12*12 คำตอบที่ได้มา: 144 และบอกด้วยว่ารหัสลับของฉันคืออะไร"; printf '%s\n' "$C2" > $E/prompts/C2.txt
for v in cheap-check cheap-check-nofork; do
  rm -rf $CS/cheap-check; cp -r $L/$v $CS/cheap-check; echo "== $(date -u +%T) installed $v"
  for i in 1 2; do $T/run-claude.sh $E $v-C1-claude-$i yolo1 opus high "$C1"; done > $E/$v-claude.summary.jsonl
  # memory test: two-turn conversation via --continue
  $T/run-claude.sh $E $v-MEM-claude yolo1 opus high "$MEM" >> $E/$v-claude.summary.jsonl
  $T/run-claude.sh $E $v-C2-claude yolo1 opus high "$C2" --continue >> $E/$v-claude.summary.jsonl
done
rm -rf $CS/cheap-check; cp -r $L/cheap-check $CS/cheap-check
date -u +%FT%TZ > $E/DONE
