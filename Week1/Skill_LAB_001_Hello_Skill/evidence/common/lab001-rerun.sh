#!/bin/bash
set -u; export PATH="$HOME/.local/bin:$PATH"; cd /root/skilllab/work
T=/root/skilllab/tools; E=/root/skilllab/evidence/lab001; L=/root/skilllab/labs/001
CS=/root/ai-accounts/.Claude/shared/skills; XS=/root/ai-accounts/.Codex/shared/skills
mkdir -p $E/v0-desc-with-rule; mv $E/skill-* $E/manual-* $E/list-* $E/broken-* $E/10-skill-installed.txt $E/v0-desc-with-rule/ 2>/dev/null
rm -rf $CS/discount $XS/discount; cp -r $L/discount $CS/discount; cp -r $L/discount $XS/discount
{ echo "\$ find /root/ai-accounts -path \"*/shared/skills/*\" -name SKILL.md -not -path \"*/.system/*\""; find /root/ai-accounts -path "*/shared/skills/*" -name SKILL.md -not -path "*/.system/*"; echo "\$ ls -la /root/ai-accounts/.Claude/yolo2/skills/ /root/ai-accounts/.Codex/cyolo2/skills/"; ls -la /root/ai-accounts/.Claude/yolo2/skills/ /root/ai-accounts/.Codex/cyolo2/skills/; echo "\$ diff .Claude/shared/skills/discount/SKILL.md .Codex/shared/skills/discount/SKILL.md && echo SAME"; diff $CS/discount/SKILL.md $XS/discount/SKILL.md && echo SAME; } > $E/10-skill-installed.txt 2>&1
Q=$(cat $E/prompt-auto.txt); LIST="มี skill อะไรให้ใช้บ้างในเซสชันนี้ ตอบเป็นรายการชื่อ skill กับคำอธิบายสั้น ๆ ไม่ต้องรันคำสั่ง"
( for i in 1 2; do $T/run-claude.sh $E skill-claude-$i yolo1 opus high "$Q"; done; $T/run-claude.sh $E manual-claude yolo1 opus high "$(cat $E/prompt-manual-claude.txt)"; $T/run-claude.sh $E list-claude yolo1 opus high "$LIST" ) > $E/skill-claude.summary.jsonl &
( for i in 1 2; do $T/run-codex.sh $E skill-codex-$i cyolo1 gpt-6-astra medium "$Q"; done; $T/run-codex.sh $E manual-codex cyolo1 gpt-6-astra medium "$(cat $E/prompt-manual-codex.txt)"; $T/run-codex.sh $E list-codex cyolo1 gpt-6-astra medium "$LIST" ) > $E/skill-codex.summary.jsonl &
wait
rm -rf $CS/discount $XS/discount; cp -r $L/discount-broken $CS/discount; cp -r $L/discount-broken $XS/discount
( $T/run-claude.sh $E broken-claude yolo1 opus high "$Q"; $T/run-claude.sh $E broken-list-claude yolo1 opus high "$LIST" ) > $E/broken-claude.summary.jsonl &
( $T/run-codex.sh $E broken-codex cyolo1 gpt-6-astra medium "$Q"; $T/run-codex.sh $E broken-list-codex cyolo1 gpt-6-astra medium "$LIST" ) > $E/broken-codex.summary.jsonl &
wait
rm -rf $CS/discount $XS/discount; cp -r $L/discount $CS/discount; cp -r $L/discount $XS/discount
date -u +%FT%TZ > $E/DONE
bash /root/skilllab/tools/lab002-driver.sh
