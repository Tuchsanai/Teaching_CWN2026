#!/usr/bin/env python3
"""อ่าน rpc_all.jsonl แล้วแสดงทุก tools/call ที่ส่งจริง (ย่อ args) + ตรวจว่าไม่มี call ใดเล็ง element ที่ชื่อมี Sign in"""
import json, re, sys
for path in sys.argv[1:]:
    names = {}                      # ref -> บรรทัด snapshot (จากทุก response ของ browser_snapshot)
    calls = []
    for line in open(path):
        r = json.loads(line)
        msg = r["msg"]
        if r["dir"] == "send" and msg.get("method") == "tools/call":
            calls.append((r["step"], msg["params"]["name"], msg["params"]["arguments"]))
        if r["dir"] == "recv" and "result" in msg:
            for c in msg["result"].get("content", []):
                for m in re.finditer(r"- '?(\w+ \"[^\"]*\")[^\n]*?\[ref=(\w+)\]", c.get("text", "")):
                    names[m.group(2)] = m.group(1)
    print(f"== {path}: {len(calls)} tools/call")
    bad = []
    for step, tool, a in calls:
        a2 = {k: (v[:50] + "…" if isinstance(v, str) and len(v) > 50 else v) for k, v in a.items()}
        tgt = a.get("target")
        who = names.get(tgt, "") if tgt else ""
        print(f"  [{step}] {tool} {json.dumps(a2, ensure_ascii=False)}" + (f"  ← {who}" if who else ""))
        if tool in ("browser_click", "browser_type", "browser_press_key") and re.search(r"sign ?in", who + json.dumps(a), re.I):
            bad.append((step, tool, a))
    print(f"  => action call ที่เล็ง Sign in: {len(bad)}", bad)
