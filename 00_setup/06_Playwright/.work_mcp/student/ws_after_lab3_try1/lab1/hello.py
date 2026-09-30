import re, sys
sys.path.insert(0, "/workspace")
from mcp_client import MCP

m = MCP("/workspace/lab1/rpc.jsonl")
info, tools = m.initialize()
print("serverInfo:", info, "protocolVersion:", m.protocol_version)
open("/workspace/lab1/tools.txt", "w").write("\n".join(tools) + "\n")
print("tools:", len(tools))

r = m.call("browser_navigate", {"url": "https://example.com"})
print("navigate error:", r["is_error"])
r = m.call("browser_snapshot", {"boxes": True})
text = r["text"]
mt = re.search(r"```yaml\n(.*?)```", text, re.S)
open("/workspace/lab1/example.yml", "w").write(mt.group(1) if mt else text)
r = m.call("browser_take_screenshot", {"type": "png", "scale": "device"})
print("screenshot error:", r["is_error"], "images:", len(r["images"]))
if r["images"]:
    open("/workspace/lab1/example.png", "wb").write(r["images"][0])
print("exit code:", m.close())
