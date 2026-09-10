#!/bin/bash
set -u; export PATH="$HOME/.local/bin:$PATH"; cd /root/skilllab/work
T=/root/skilllab/tools; E=/root/skilllab/evidence/lab007; L=/root/skilllab/labs/007
CS=/root/ai-accounts/.Claude/shared/skills; XS=/root/ai-accounts/.Codex/shared/skills
mkdir -p $E/prompts $E/generated
for s in discount accounts shop-rules cheap-check vat second-opinion second-opinion-ai; do rm -rf $CS/$s $XS/$s; done
Q="ขอความเห็นที่สองว่าซื้อของ 1000 บาท ลด 10% ต้องจ่ายเท่าไร"; printf '%s\n' "$Q" > $E/prompts/Q.txt
# ---- Phase A: hand-written ----
cp -r $L/second-opinion $CS/second-opinion; cp -r $L/second-opinion-codex $XS/second-opinion; echo "== $(date -u +%T) hand-written installed"
( for i in 1 2 3; do $T/run-claude.sh $E hand-Q-claude-$i yolo1 opus high "$Q"; done ) > $E/hand-claude.summary.jsonl
( for i in 1 2 3; do $T/run-codex.sh  $E hand-Q-codex-$i cyolo1 gpt-6-astra medium "$Q"; done ) > $E/hand-codex.summary.jsonl
rm -rf $CS/second-opinion $XS/second-opinion
# ---- Phase B: AI-generated (Claude writes for Claude side; Codex skill-creator writes for Codex side) ----
echo "== $(date -u +%T) generating with Claude (yolo1)"
$T/run-claude.sh $E gen-claude yolo1 opus high "$(cat $L/prompts/spec-claude.txt)" > $E/gen-claude.summary.jsonl
[ -d $CS/second-opinion-ai ] && cp -r $CS/second-opinion-ai $E/generated/claude-second-opinion-ai
echo "== $(date -u +%T) generating with Codex skill-creator (cyolo1)"
$T/run-codex.sh $E gen-codex cyolo1 gpt-6-astra medium "$(cat $L/prompts/spec-codex.txt)" > $E/gen-codex.summary.jsonl
[ -d $XS/second-opinion-ai ] && cp -r $XS/second-opinion-ai $E/generated/codex-second-opinion-ai
ls -R $E/generated > $E/generated-tree.txt 2>&1
# validate with skill-creator's validator
for d in $E/generated/*; do echo "== validate $d"; python3 $XS/.system/skill-creator/scripts/quick_validate.py "$d" 2>&1; done > $E/quick-validate.txt
# ---- Phase B runs ----
( for i in 1 2 3; do $T/run-claude.sh $E ai-Q-claude-$i yolo1 opus high "$Q"; done ) > $E/ai-claude.summary.jsonl
( for i in 1 2 3; do $T/run-codex.sh  $E ai-Q-codex-$i cyolo1 gpt-6-astra medium "$Q"; done ) > $E/ai-codex.summary.jsonl
date -u +%FT%TZ > $E/DONE
