#!/bin/bash
set -u; export PATH="$HOME/.local/bin:$PATH"; cd /root/skilllab/work
T=/root/skilllab/tools; E=/root/skilllab/evidence/lab003; L=/root/skilllab/labs/003
CS=/root/ai-accounts/.Claude/shared/skills; XS=/root/ai-accounts/.Codex/shared/skills
mkdir -p $E/prompts
inst() { rm -rf $CS/discount $XS/discount; cp -r "$L/$1" $CS/discount; cp -r "$L/$1" $XS/discount; echo "== $(date -u +%T) installed $1"; }
A2="/discount 1500 10"; A1="/discount 1500"; AQ='/discount "1 500" 10'
printf '%s\n' "$A2" > $E/prompts/A2.txt; printf '%s\n' "$A1" > $E/prompts/A1.txt; printf '%s\n' "$AQ" > $E/prompts/AQ.txt
X2='$discount 1500 10'; printf '%s\n' "$X2" > $E/prompts/X2.txt
for v in args-plain args-index args-named; do
  inst $v
  ( $T/run-claude.sh $E $v-A2-claude yolo1 opus high "$A2"; $T/run-claude.sh $E $v-A1-claude yolo1 opus high "$A1" ) > $E/$v-claude.summary.jsonl &
  ( $T/run-codex.sh $E $v-X2-codex cyolo1 gpt-6-astra medium "$X2" ) > $E/$v-codex.summary.jsonl &
  wait
done
inst args-index
$T/run-claude.sh $E args-index-AQ-claude yolo1 opus high "$AQ" > $E/args-index-AQ-claude.summary.jsonl
date -u +%FT%TZ > $E/DONE
