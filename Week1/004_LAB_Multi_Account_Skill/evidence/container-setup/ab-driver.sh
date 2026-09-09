#!/bin/bash
# usage: ab-driver.sh <phase>  (phase = noskill | skill) ; sequential: 2x Claude shell, 2x Codex shell
set -u; phase=$1; cd /root/lab004; mkdir -p ab; : > "ab/$phase.summary.jsonl"
for i in 1 2; do echo "{\"tag\":\"$phase-claude-$i\",$(bash ab-claude.sh $phase-claude-$i prompt-step3.txt | cut -c2-)" >> "ab/$phase.summary.jsonl"; done
for i in 1 2; do echo "{\"tag\":\"$phase-codex-$i\",$(bash ab-codex.sh $phase-codex-$i prompt-step4.txt | cut -c2-)" >> "ab/$phase.summary.jsonl"; done
date -u +%FT%TZ > "ab/$phase.done"
