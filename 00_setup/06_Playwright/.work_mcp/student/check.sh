#!/bin/bash
# bash check.sh N → รันคำสั่ง "วิธีตรวจ" ของ README ใน container
C=devtools-pwmcp-c34a6add
case $1 in
1) CMD='python3 -c "import json;print(json.load(open(\"/workspace/mcp.config.json\"))[\"browser\"][\"browserName\"])"; wc -l lab1/tools.txt; grep -n "Learn more" lab1/example.yml; head -c 400 lab1/rpc.jsonl; echo; grep -c "bytes image/png" lab1/rpc.jsonl; ps aux | grep -c [c]hrom; cat lab1/lab1.txt; ls -la lab1; python3 -c "import struct;d=open(\"lab1/example.png\",\"rb\").read(24);print(struct.unpack(\">II\",d[16:24]))"';;
2) CMD='ls -la lab2; wc -l lab2/*.yml lab2/form.txt; grep -c "### Snapshot" lab2/responses.txt; cat lab2/form.txt; head -15 lab2/find.txt; head -8 lab2/form-partial.yml; python3 -c "import struct;d=open(\"lab2/flights.png\",\"rb\").read(24);print(struct.unpack(\">II\",d[16:24]))"; grep -c "\"isError\": true" lab2/rpc.jsonl; ps aux | grep -c [c]hrom';;
3) CMD='ls -la lab3; grep -n "One way\|BKK" lab3/final.yml; grep -c "\[expanded\]" lab3/final.yml; grep -c "await page" lab3/actions.txt; grep -c "await page.getBy" lab3/actions.txt; grep -n "browser_type" -A3 lab3/actions.txt; grep -c "\"isError\": true" lab3/rpc.jsonl; ps aux | grep -c [c]hrom';;
4) CMD='ls -la lab4; grep -n -A1 "not found" lab4/stale.txt; grep -c "\"isError\": true" lab4/rpc.jsonl; grep -c "\"error\"" lab4/rpc.jsonl; grep -n "ticket type" lab4/old.yml lab4/new.yml; ps aux | grep -c [c]hrom';;
5) CMD='ls lab5/step/; grep -c innerHTML lab5/one_step.py; grep -c disallowedTools lab5/one_step.py; grep -o "\"name\": \"browser_[a-z_]*\"" lab5/step/rpc.jsonl | sort | uniq -c; grep -n "One way" lab5/step/verify.yml; cat lab5/step/act.txt; ps aux | grep -c [c]hrom';;
6) CMD='head -2 log/run.log; tail -1 log/run.log; ls log/steps/; grep -c "\"isError\": true" log/rpc_all.jsonl; cat log/run.log; ps aux | grep -c [c]hrom';;
7) CMD='grep -c "\"name\": \"browser_click\"" log/guardrail/A/rpc_all.jsonl; grep -rn "AI assistant" log/guardrail/B/steps/*/prompt.txt | cut -c1-200; grep -rih "sign in" log/guardrail/B/steps/*/act.txt; tail -3 log/guardrail/check_no_signin.txt; cat log/guardrail/A/run.log log/guardrail/B/run.log; ps aux | grep -c [c]hrom';;
esac
docker exec $C bash -lc "cd /workspace && $CMD" 2>&1
