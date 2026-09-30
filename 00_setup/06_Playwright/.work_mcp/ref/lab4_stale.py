#!/usr/bin/env python3
"""LAB 4 (อ้างอิง): พิสูจน์ว่า ref ใช้ได้กับ snapshot ล่าสุดเท่านั้น ผ่าน Playwright MCP
ผล: runs/lab4/ old.yml new.yml new.png stale.txt (ทุก tools/call + ข้อความตอบจริง + isError) rpc.jsonl"""
import re, sys, time
from pathlib import Path

from mcp_client import MCP, snapshot_yaml, write_config

URL = "https://www.google.com/travel/flights?hl=en"
out = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/lab4").resolve()
out.mkdir(parents=True, exist_ok=True)
log = open(out / "stale.txt", "w")
m = MCP(write_config(out / "mcp.config.json", out / "mcp-out"), out / "rpc_all.jsonl", cwd=str(out))
m.set_step_log(out / "rpc.jsonl", "lab4")
m.initialize()


def call(tool, args):
    r = m.call(tool, args)
    log.write(f"→ tools/call {tool} {args}\n{r['text'].rstrip()}\n[isError: {str(r['is_error']).lower()}]\n\n")
    log.flush()
    return r


def ref_of(snap, rx):
    mm = re.search(rx + r'.*?\[ref=(\w+)\]', snap)
    return mm.group(1) if mm else None


call("browser_navigate", {"url": URL})
time.sleep(2)
old = snapshot_yaml(call("browser_snapshot", {"boxes": True})["text"])
(out / "old.yml").write_text(old)
OLD = ref_of(old, r'combobox "Change ticket type')
log.write(f"# OLD = {OLD}\n\n")
call("browser_click", {"target": OLD})
s = snapshot_yaml(call("browser_snapshot", {})["text"])
call("browser_click", {"target": ref_of(s, r'option "One way"')})
time.sleep(1)
call("browser_click", {"target": OLD})                                   # ref เก่า → คาดว่า isError
new = snapshot_yaml(call("browser_snapshot", {"boxes": True})["text"])
(out / "new.yml").write_text(new)
r = m.call("browser_take_screenshot", {"type": "png", "scale": "device"})
(out / "new.png").write_bytes(r["images"][0])
log.write(f"→ tools/call browser_take_screenshot {{'type': 'png', 'scale': 'device'}}\n(image block {len(r['images'][0])} bytes → new.png)\n\n")
NEW = ref_of(new, r'combobox "Change ticket type')
log.write(f"# NEW = {NEW}\n\n")
call("browser_click", {"target": NEW})
call("browser_press_key", {"key": "Escape"})
log.write(f"# exit {m.close()}\n")
for name, s in (("old.yml", old), ("new.yml", new)):
    print(name, [l.strip() for l in s.splitlines() if "ticket type" in l])
