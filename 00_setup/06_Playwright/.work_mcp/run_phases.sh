#!/bin/bash
# รันเฟสตามลำดับ: bash run_phases.sh 2 3 4 5
cd /root/workspace/CWN/Teaching/00_setup
W=06_Playwright/.work_mcp
for p in "$@"; do
  echo "$(date +%T) START phase$p" >> $W/phases.log
  yolo1 -p --model opus --effort medium --strict-mcp-config --output-format json "$(cat $W/phase${p}_prompt.txt)" < /dev/null > $W/phase${p}_result.json 2> $W/phase${p}_err.log
  python3 -c "import json;d=json.load(open('$W/phase${p}_result.json'));print('phase$p is_error',d.get('is_error'),'turns',d.get('num_turns'),'cost',d.get('total_cost_usd'))" >> $W/phases.log 2>&1
  echo "$(date +%T) END phase$p" >> $W/phases.log
  python3 -c "import json,sys;d=json.load(open('$W/phase${p}_result.json'));sys.exit(1 if d.get('is_error') else 0)" || { echo "STOP phase$p error" >> $W/phases.log; exit 1; }
done
echo "$(date +%T) ALL_DONE" >> $W/phases.log
