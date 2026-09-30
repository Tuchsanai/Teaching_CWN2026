#!/bin/bash
# รอ LAB 2 จบ แล้ว resume session เฟส 5 ให้ทำต่อแบบ foreground
cd /root/workspace/CWN/Teaching/00_setup
W=06_Playwright/.work_mcp
# no wait
echo "$(date +%T) START phase5b" >> $W/phases.log
yolo1 -p --model opus --effort medium --strict-mcp-config --output-format json --resume "$(cat $W/phase5_session.txt)" "$(cat $W/phase5b_prompt.txt)" < /dev/null > $W/phase5b_result.json 2> $W/phase5b_err.log
python3 -c "import json;d=json.load(open('$W/phase5b_result.json'));print('phase5b is_error',d.get('is_error'),'turns',d.get('num_turns'),'cost',d.get('total_cost_usd'))" >> $W/phases.log 2>&1
echo "$(date +%T) END phase5b" >> $W/phases.log
