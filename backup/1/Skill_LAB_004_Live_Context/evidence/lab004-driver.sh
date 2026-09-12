#!/bin/bash
set -u; export PATH="$HOME/.local/bin:$PATH"; cd /root/skilllab/work
T=/root/skilllab/tools; E=/root/skilllab/evidence/lab004; L=/root/skilllab/labs/004
CS=/root/ai-accounts/.Claude/shared/skills; XS=/root/ai-accounts/.Codex/shared/skills
mkdir -p $E/prompts
rm -rf $CS/discount $XS/discount
Q="บัญชีไหนล็อกอินอยู่บ้างตอนนี้ ตอบเป็นตาราง"; printf '%s\n' "$Q" > $E/prompts/Q.txt
M="/accounts"; printf '%s\n' "$M" > $E/prompts/M.txt
rm -rf $CS/accounts $XS/accounts; cp -r $L/accounts $CS/accounts; cp -r $L/accounts-codex $XS/accounts; echo "== installed accounts (claude: inject, codex: script)"
( time bash $CS/accounts/scripts/status.sh ) > $E/00-status-script-output.txt 2>&1
( for i in 1 2; do $T/run-claude.sh $E inject-Q-claude-$i yolo1 opus high "$Q"; done; $T/run-claude.sh $E inject-M-claude yolo1 opus high "$M" ) > $E/inject-claude.summary.jsonl &
( for i in 1 2; do $T/run-codex.sh $E script-Q-codex-$i cyolo1 gpt-6-astra medium "$Q"; done; $T/run-codex.sh $E script-M-codex cyolo1 gpt-6-astra medium '$accounts' ) > $E/script-codex.summary.jsonl &
wait
echo "== naive variant (exit 1 inside !cmd)"
rm -rf $CS/accounts; cp -r $L/accounts-naive $CS/accounts
$T/run-claude.sh $E naive-M-claude yolo1 opus high "$M" > $E/naive-claude.summary.jsonl
$T/run-claude.sh $E naive-Q-claude yolo1 opus high "$Q" >> $E/naive-claude.summary.jsonl
echo "== disableSkillShellExecution"
rm -rf $CS/accounts; cp -r $L/accounts $CS/accounts
SJ=/root/ai-accounts/.Claude/yolo1/settings.json; [ -e $SJ ] && cp $SJ $SJ.bak
printf '{"disableSkillShellExecution": true}\n' > $SJ
$T/run-claude.sh $E disabled-M-claude yolo1 opus high "$M" > $E/disabled-claude.summary.jsonl
if [ -e $SJ.bak ]; then mv $SJ.bak $SJ; else rm -f $SJ; fi
date -u +%FT%TZ > $E/DONE
