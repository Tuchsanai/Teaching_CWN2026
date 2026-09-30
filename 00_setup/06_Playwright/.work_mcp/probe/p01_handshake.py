import json, sys
from mcp_client import MCPClient
MCP = ["/usr/bin/playwright-mcp", "--config", "mcp.config.json"]
c = MCPClient(MCP, "p01_handshake.jsonl")
init = c.initialize()
tl = c.list_tools()
tools = tl["result"]["tools"]
json.dump({"initialize_result": init["result"], "tools": tools}, open("tools.json", "w"), indent=1, ensure_ascii=False)
with open("tools_table.md", "w") as f:
    f.write("| # | tool | required | properties | readOnlyHint/destructiveHint | description (บรรทัดแรก) |\n|---|---|---|---|---|---|\n")
    for i, t in enumerate(tools, 1):
        s = t.get("inputSchema", {})
        props = ", ".join(s.get("properties", {}).keys())
        ann = t.get("annotations", {})
        f.write(f"| {i} | `{t['name']}` | {', '.join(s.get('required', [])) or '-'} | {props or '-'} | "
                f"{ann.get('readOnlyHint')}/{ann.get('destructiveHint')} | {t.get('description','').splitlines()[0][:90]} |\n")
print("tools/list bytes:", tl["_bytes"], "n tools:", len(tools))
c.close()
# ลองขอ protocolVersion ที่ไม่มี / เก่า
for pv in ["2024-11-05", "1999-01-01"]:
    c = MCPClient(MCP, f"p01_protocol_{pv}.jsonl")
    r = c.request("initialize", {"protocolVersion": pv, "capabilities": {}, "clientInfo": {"name": "p", "version": "0"}})
    print(pv, "->", json.dumps(r.get("result", r.get("error")))[:200])
    c.close()
# caps เพิ่ม
c = MCPClient(MCP + ["--caps", "vision,pdf,devtools"], "p01_caps.jsonl")
c.initialize()
names = [t["name"] for t in c.list_tools()["result"]["tools"]]
base = {t["name"] for t in tools}
print("extra with --caps vision,pdf,devtools:", [n for n in names if n not in base])
c.close()
# ลองเรียก tools/call ก่อน initialize
c = MCPClient(MCP, "p01_call_before_init.jsonl")
r = c.call("browser_snapshot", {}, timeout=60)
print("call before init:", json.dumps(r)[:300])
c.close()
