#!/bin/bash
# bash tools_used.sh <session_id> → รายชื่อ tool ที่ yolo1 เรียกในเซสชันนั้น
docker exec devtools-pwmcp-c34a6add bash -lc "cat /root/ai-accounts/.Claude/yolo1/projects/-workspace/$1.jsonl" | python3 -c '
import json,sys
for l in sys.stdin:
    try: d=json.loads(l)
    except: continue
    m=d.get("message") or {}
    if d.get("type")=="assistant" and isinstance(m.get("content"),list):
        for c in m["content"]:
            if c.get("type")=="tool_use":
                i=c["input"]; s=i.get("command") or i.get("file_path") or json.dumps(i,ensure_ascii=False)
                print(c["name"], "|", str(s).replace("\n"," ")[:160])
'
