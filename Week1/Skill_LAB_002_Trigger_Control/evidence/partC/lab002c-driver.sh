#!/bin/bash
# LAB 002 part C: does Codex ignore the Claude-only field disable-model-invocation? (prompt allows commands)
set -u; export PATH="$HOME/.local/bin:$PATH"; cd /root/skilllab/work
T=/root/skilllab/tools; E=/root/skilllab/evidence/lab002c; L=/root/skilllab/labs/002
CS=/root/ai-accounts/.Claude/shared/skills; XS=/root/ai-accounts/.Codex/shared/skills
mkdir -p $E; for s in discount accounts shop-rules cheap-check vat second-opinion second-opinion-ai; do rm -rf $CS/$s $XS/$s; done
cp -r $L/no-model $XS/discount; cp -r $L/no-model $CS/discount
P1="ซื้อของ 1500 บาท ต้องจ่ายกี่บาท ตอบสั้น ๆ ไม่ต้องสร้างไฟล์"
( for i in 1 2; do $T/run-codex.sh $E no-model-P1-codex-$i cyolo1 gpt-6-astra medium "$P1"; done ) > $E/no-model-codex.summary.jsonl
rm -rf $CS/discount $XS/discount
date -u +%FT%TZ > $E/DONE
